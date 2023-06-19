import datetime
import logging
import os
import tempfile

import click
from pyoscar import OSCARClient

from synop import db
from synop.config import SETTINGS
from synop.constants import COUNTRIES
from synop.models import Station, StationIdentifier
from synop.utils import read_state, get_next_available_timestep, convert_bufr3, bufr2geojson, load_obs_from_geojson, \
    update_state

DATASETS_DIR = SETTINGS.get("DATASETS_DIR")


@click.command(name="load_stations")
def load_stations():
    logging.info("[STATIONS_LOADING]: Loading stations")

    client = OSCARClient()

    for country in COUNTRIES:
        country_iso = country.get("iso")

        try:
            logging.info(f"[STATIONS_LOADING]: Loading stations for country {country_iso}")

            stations = client.get_stations(country=country_iso)
            results = stations.get("stationSearchResults")

            for station in results:
                wigos_id = station.get("wigosId")
                longitude = station.get("longitude")
                latitude = station.get("latitude")

                wigos_station_identifiers = station.get("wigosStationIdentifiers")

                if not wigos_id and wigos_station_identifiers:
                    wigos_id = wigos_station_identifiers[0].get("wigosStationIdentifier")

                if not wigos_id and not longitude and latitude:
                    continue

                station_data = {
                    "wigos_id": wigos_id,
                    "name": station.get("name"),
                    "territory": station.get("territory"),
                    "elevation": station.get("elevation"),
                    "longitude": station.get("longitude"),
                    "latitude": station.get("latitude"),
                }

                db_station = Station.query.get(station_data.get("wigos_id"))
                exists = False

                if db_station:
                    exists = True

                db_station = Station(**station_data)

                if exists:
                    logging.info('[STATION]: UPDATE')
                    db.session.merge(db_station)
                else:
                    logging.info('[STATION]: ADD')
                    db.session.add(db_station)

                db.session.commit()

                if wigos_station_identifiers:
                    for identifier in wigos_station_identifiers:
                        if not identifier.get("primary"):
                            station_identifier = identifier.get("wigosStationIdentifier")
                            station_id_data = {
                                "wigos_id": wigos_id,
                                "identifier": station_identifier
                            }

                            station_id = StationIdentifier.query.filter_by(identifier=station_identifier).first()
                            exists = False

                            if station_id:
                                exists = True

                            station_id = StationIdentifier(**station_id_data)

                            if exists:
                                logging.info('[STATION ID]: UPDATE')
                                db.session.merge(station_id)
                            else:
                                logging.info('[STATION ID]: ADD')
                                db.session.add(station_id)
                            db.session.commit()

        except Exception as e:
            logging.error(e)
            db.session.rollback()
            pass


@click.command(name="load_observations")
def load_observations():
    if os.path.exists(DATASETS_DIR):
        state = read_state()

        last_update = state.get("last_update")

        if last_update:
            next_update = get_next_available_timestep(last_update)
        else:
            date_str = datetime.datetime.now().isoformat()
            next_update = get_next_available_timestep(date_str)

        if next_update:
            next_update_str = next_update.isoformat()
            logging.info(f'[OBS]: Trying ingestion for date {next_update_str}...')
            d_str = next_update.strftime("%Y%m%d%H%M")

            f_name = f"SYNA0001_{d_str}_180.DAT"

            file_path = os.path.join(DATASETS_DIR, f_name)

            if os.path.exists(file_path):
                logging.info(f'[OBS]: Found data for date: {next_update_str}. Starting processing..')
                with tempfile.TemporaryDirectory() as temp_dir:
                    out_bufr4 = os.path.join(temp_dir, "out.DAT")

                    logging.info(f"[OBS]: Converting '{f_name}' to bufr edition 4...")
                    convert_bufr3(file_path, out_bufr4)

                    logging.info(f"[OBS]: Converting to Geojson...")
                    geojson = bufr2geojson(out_bufr4, next_update_str)

                logging.info(f"[OBS]: Ingesting to database...")
                # load observation to databaset
                load_obs_from_geojson(geojson)

                logging.info(f"[OBS]: Updating state...")
                # update state
                update_state(next_update_str)

            else:
                logging.warning(f'[OBS]: Data not found for date: {next_update_str}. Skipping...')
