import logging

import pytz
from flask import request, jsonify
from sqlalchemy import and_, func

from synop import db
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
@endpoints.route('/statistics', strict_slashes=False, methods=['GET'])
def get_statistics():
    logging.info(f'[ROUTER]: Getting statistics')

    args = request.args
    date = args.get('date')
    parameters = args.get('parameters')

    if not date:
        # get latest available date
        date = Observation.query.with_entities(Observation.time).distinct().order_by(Observation.time.desc()).first()

    if not parameters:
        return jsonify('No parameters provided'), 400

    if isinstance(parameters, str):
        parameters = [parameters]

    for param in parameters:
        if not hasattr(Observation, param):
            return jsonify({"error": f"Invalid parameter: {param}"}), 400

    # Construct the query
    try:
        query_filters = [Observation.time == date]
        for param in parameters:
            query_filters.append(getattr(Observation, param) != None)

        # Join with Station table to get territory
        query = db.session.query(
            Station.territory,
            func.count(Observation.wigos_id.distinct()).label('station_count')
        ).join(
            Observation, Observation.wigos_id == Station.wigos_id
        ).filter(
            and_(*query_filters)
        ).group_by(
            Station.territory
        ).all()

        # Format the results
        results = {territory: count for territory, count in query}

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
