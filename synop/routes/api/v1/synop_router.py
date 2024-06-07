import logging

import pytz
from flask import jsonify
from flask import request

from synop.models import Observation, Station
from synop.routes.api.v1 import endpoints


@endpoints.route('/dates', strict_slashes=False, methods=['GET'])
def get_available_dates():
    logging.info('[ROUTER]: Getting available dates')

    distinct_dates = Observation.query.with_entities(Observation.time).distinct().order_by(Observation.time).all()
    response = [date[0].replace(tzinfo=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z") for date in distinct_dates]

    return jsonify(response), 200


# Download country Stations data as csv
@endpoints.route('/stations', strict_slashes=False, methods=['GET'])
def get_country_stations_data():
    args = request.args
    country = args.get('country')
    data_format = args.get('format')

    if not country:
        stations = Station.query.all()
    else:
        stations = Station.query.filter_by(territory=country).all()

    if not stations:
        logging.error(f'[ROUTER]: No stations found')
        return jsonify(f'No stations found for country'), 404

    if data_format == 'geojson':
        stations = {
            "type": "FeatureCollection",
            "features": [station.serialize(as_geojson=True) for station in stations],
        }
    else:
        stations = [station.serialize() for station in stations]

    return jsonify(stations), 200


# Download gts data as csv
@endpoints.route('/download', strict_slashes=False, methods=['GET'])
def get_country_observation_data():
    logging.info('[ROUTER]: Downloading station data')

    return jsonify('Not implemented yet'), 501


# get statistics for a specific date
@endpoints.route('/statistics/<string:date>', strict_slashes=False, methods=['GET'])
def get_statistics(date):
    logging.info(f'[ROUTER]: Getting statistics for date: {date}')

    return jsonify('Not implemented yet'), 501
