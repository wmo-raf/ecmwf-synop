import logging

from flask import jsonify
from sqlalchemy import func

from synop.models import Observation
from synop.routes.api.v1 import endpoints


@endpoints.route('/dates', strict_slashes=False, methods=['GET'])
def get_available_dates():
    logging.info('[ROUTER]: Getting available dates')

    distinct_dates = Observation.query.with_entities(func.date(Observation.time)).distinct().all()
    response = distinct_dates

    return jsonify(response), 200
