import json
import logging
import os
import shutil
import stat
import tempfile
from datetime import datetime, timedelta
from subprocess import Popen, PIPE

from bufr2geojson import transform as as_geojson
from sqlalchemy.exc import IntegrityError

from synop import db
from synop.config import SETTINGS
from synop.models import Station, StationIdentifier, Observation
from synop.models.synop import rename_columns

STATE_DIR = SETTINGS.get("STATE_DIR")
STATE_FILE = os.path.join(STATE_DIR, "state.json")


def copy_with_metadata(source, target):
    """Copy file with all its permissions and metadata.

    Lifted from https://stackoverflow.com/a/43761127/2860309
    :param source: source file name
    :param target: target file name
    """
    # copy content, stat-info (mode too), timestamps...
    shutil.copy2(source, target)
    # copy owner and group
    st = os.stat(source)
    os.chown(target, st[stat.ST_UID], st[stat.ST_GID])


def atomic_write(file_contents, target_file_path, mode="w"):
    """Write to a temporary file and rename it to avoid file corruption.
    Attribution: @therightstuff, @deichrenner, @hrudham
    :param file_contents: contents to be written to file
    :param target_file_path: the file to be created or replaced
    :param mode: the file mode defaults to "w", only "w" and "a" are supported
    """
    # Use the same directory as the destination file so that moving it across
    # file systems does not pose a problem.
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        dir=os.path.dirname(target_file_path))
    try:
        # preserve file metadata if it already exists
        if os.path.exists(target_file_path):
            copy_with_metadata(target_file_path, temp_file.name)
        with open(temp_file.name, mode) as f:
            f.write(file_contents)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_file.name, target_file_path)
    finally:
        if os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


def write_empty_state():
    content = {"last_update": ""}
    atomic_write(json.dumps(content, indent=4), STATE_FILE)
    return content


def read_state():
    # create state file if it does not exist
    if not os.path.isfile(STATE_FILE):
        with open(STATE_FILE, mode='w') as f:
            f.write("{}")
    try:
        logging.debug(f"[STATE]: Opening state file {STATE_FILE}")
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    except json.decoder.JSONDecodeError:
        state = write_empty_state()

    return state


def update_state(last_update):
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)

    state.update({"last_update": last_update})

    atomic_write(json.dumps(state, indent=4), STATE_FILE)


def get_next_available_timestep(datetime_str):
    input_datetime = datetime.fromisoformat(datetime_str)
    current_time = input_datetime.replace(minute=0, second=0, microsecond=0)

    if current_time.hour % 3 != 0:
        current_time += timedelta(hours=3 - (current_time.hour % 3))

    while current_time <= input_datetime:
        current_time += timedelta(hours=3)

    return current_time


def convert_bufr3(input_file, output_file):
    cmd = ["bufr_set", "-s", "edition=4", input_file, output_file]

    p1 = Popen(cmd, stdout=PIPE, stderr=PIPE)

    p1.stdout.close()

    stdout, stderr = p1.communicate()

    if stderr:
        raise Exception(stderr)


def bufr2geojson(bufr_path, time_str):
    with open(bufr_path, "rb") as fh:
        logging.debug('Procesing BUFR data')

        logging.debug('Generating GeoJSON features')
        results = as_geojson(fh.read(), serialize=False)

        feature_collection = {}

        geojson = {"type": "FeatureCollection", "features": []}

        logging.debug('Processing GeoJSON features')
        for collection in results:
            for _, item in collection.items():
                logging.debug('Parsing feature datetime')
                data_date = item['_meta']['data_date']
                if '/' in data_date:
                    # date is range/period, split and get end date/time
                    data_date = data_date.split('/')[1]

                logging.debug('Parsing feature fields')
                items_to_remove = [
                    key for key in item if key not in ('geojson', '_meta')
                ]
                for key in items_to_remove:
                    logging.debug(f'Removing unexpected key: {key}')
                    item.pop(key)

                if item.get("geojson"):
                    feature = item.get("geojson")
                    f_properties = feature.get("properties")

                    wigos_id = f_properties.get("wigos_station_identifier")

                    if feature_collection.get(wigos_id) is None:
                        feature_collection[wigos_id] = {**feature, "properties": {}}

                    feature_collection[wigos_id]["id"] = wigos_id

                    final_properties = feature_collection[wigos_id].get("properties")

                    time = time_str
                    name = f_properties.get("name")
                    value = f_properties.get("value")

                    if time:
                        final_properties.update({"time": time})

                    if name and value:
                        final_properties.update({name: value})

                    feature_collection[wigos_id]["properties"] = final_properties

        for station_id, feature in feature_collection.items():
            geojson["features"].append(feature)

    return geojson


def load_obs_from_geojson(geojson):
    for feature in geojson.get("features"):
        wigos_id = feature.get("id")
        station = Station.query.get(wigos_id)

        if not station:
            identifier = StationIdentifier.query.filter_by(identifier=wigos_id).first()

            if identifier:
                wigos_id = identifier.wigos_id
                station = Station.query.get(wigos_id)

        if station:
            properties = feature.get("properties")

            for key in list(properties):
                if rename_columns.get(key):
                    new_col_name = rename_columns.get(key)
                    properties.update({new_col_name: properties[key]})

            obs = Observation(**properties, wigos_id=station.wigos_id)

            try:
                logging.info('[OBSERVATION]: ADD')
                db.session.add(obs)
                db.session.commit()
            except IntegrityError:
                obs = Observation.query.filter_by(wigos_id=wigos_id, time=properties.get("time")).first()

                for key, val in properties.items():
                    if hasattr(obs, key):
                        setattr(obs, key, val)

                logging.info('[OBSERVATION]: ADD')
                db.session.merge(obs)
                db.session.commit()
            except Exception as e:
                logging.info('[OBSERVATION]: Error adding or updating')
                db.session.rollback()
