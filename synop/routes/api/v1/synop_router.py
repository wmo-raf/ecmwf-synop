import logging

import pytz
from flask import jsonify

from synop.models import Observation
from synop.routes.api.v1 import endpoints


@endpoints.route('/dates', strict_slashes=False, methods=['GET'])
def get_available_dates():
    logging.info('[ROUTER]: Getting available dates')

    distinct_dates = Observation.query.with_entities(Observation.time).distinct().order_by(Observation.time).all()
    response = [date[0].replace(tzinfo=pytz.UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ') for date in distinct_dates]

    return jsonify(response), 200
