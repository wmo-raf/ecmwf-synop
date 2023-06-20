import logging

from flask import jsonify

from synop.models import Observation
from synop.routes.api.v1 import endpoints


@endpoints.route('/dates', strict_slashes=False, methods=['GET'])
def get_available_dates():
    logging.info('[ROUTER]: Getting available dates')

    distinct_dates = Observation.query.with_entities(Observation.time).distinct().all()
    response = [date[0].isoformat() for date in distinct_dates]

    return jsonify(response), 200
