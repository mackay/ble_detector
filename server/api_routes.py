from bottle import hook
from bottle import request, post

from core.apiutil import require_fields, serialize_json
from core.detector import DetectorProcess
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
@post('/detector')
@require_fields(["uuid"])
@serialize_json()
def post_detector():
    body = request.json
    detector_process = DetectorProcess(body["uuid"])
    status_dictionary = body["status_dictionary"] if "status_dictionary" in body else None

    return detector_process.checkin(status_dictionary=status_dictionary)


# POST /rssi
@post('/signal')
@require_fields(["detector_uuid", "beacon_uuid", "rssi"])
@serialize_json()
def post_signal():
    body = request.json

    source_data = body["source_data"] if "source_data" in body else None

    detector_process = DetectorProcess(body["detector_uuid"])
    return detector_process.add_signal(body["beacon_uuid"], body["rssi"], source_data=source_data)


# GET /beacon

# GET /beacon/<addr>

# POST /training

# DEL /training

@post('/option')
@require_fields(["key", "value"])
@serialize_json()
def post_mode():
    body = request.json

    try:
        system_option = SystemOption.get(SystemOption.key == body["key"])
    except:
        system_option = SystemOption()

    system_option.value = body["value"]
    system_option.key = body["key"]
    system_option.save()

    return system_option
