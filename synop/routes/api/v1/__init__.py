from flask import Blueprint, jsonify


# GENERIC Error
def error(status=400, detail='Bad Request'):
    return jsonify({
        'status': status,
        'detail': detail
    }), status


endpoints = Blueprint('endpoints', __name__)

import synop.routes.api.v1.synop_router
