from bottle import hook
from bottle import request, post

from core.apiutil import require_fields, serialize_json
from core.detector import DetectorAgent
from core.system import SystemBase
from core.models import database, SystemOption


import logging
log = logging.getLogger()


@hook('before_request')
def before_request():
    database.connect()


@hook('after_request')
def after_request():
    database.close()


# POST /detector
@post('/detector', is_api=True)
@require_fields(["uuid"])
@serialize_json()
def post_detector():
    body = request.json
    detector_agent = DetectorAgent(body["uuid"])
    status_dictionary = body["status_dictionary"] if "status_dictionary" in body else None

    return detector_agent.checkin(status_dictionary=status_dictionary)


# POST /rssi
@post('/signal', is_api=True)
@require_fields(["detector_uuid", "beacon_uuid", "rssi"])
@serialize_json()
def post_signal():
    body = request.json

    source_data = body["source_data"] if "source_data" in body else None

    detector_agent = DetectorAgent(body["detector_uuid"])
    return detector_agent.add_signal(body["beacon_uuid"], body["rssi"], source_data=source_data)


# GET /beacon

# GET /beacon/<addr>

# POST /training

# DEL /training

@post('/option', is_api=True)
@require_fields(["key", "value"])
@serialize_json()
def post_mode():
    body = request.json
    return SystemBase().set_option(body["key"], body["value"])
