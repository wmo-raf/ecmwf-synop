import logging

from flask import jsonify, request

from synop.routes.api.v1 import endpoints


@endpoints.route('/stations', strict_slashes=False, methods=['GET'])
def get_stations():
    logging.info('[ROUTER]: Getting all stations')

    include = request.args.get('include')

    response = {
        "data": [],
        "total": None,
        "has_next": None,
        "has_prev": None,
        "page": None
    }

    return jsonify(**response), 200
