from bottle import hook
from bottle import abort
from bottle import request, post, delete, get

from core.apiutil import require_fields, serialize_json

from core.models import database

from core.system import SystemBase
from core.detector import DetectorAgent
from core.training import TrainingNetwork, TrainingDetectorAgent


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

    #if we're off, don't accept anything
    if SystemBase().is_mode_off():
        abort(503, "Signal posting not allowed when system is in 'off' mode")

    #if we don't fit the filter, dump the signal
    beacon_filter = SystemBase().get_option(SystemBase.FILTER_KEY)
    if beacon_filter and beacon_filter not in body["beacon_uuid"]:
        abort(409, "Beacon UUID {uuid} not acceptable to current server filter: {filter}".format(
            uuid=body["beacon_uuid"],
            filter=beacon_filter))

    if SystemBase().is_mode_training():
        detector_agent = TrainingDetectorAgent(body["detector_uuid"])
    else:
        detector_agent = DetectorAgent(body["detector_uuid"])

    return detector_agent.add_signal(body["beacon_uuid"], body["rssi"], source_data=source_data)


# GET /beacon

# GET /beacon/<addr>

# POST /training

# DEL /training
@delete('/training', is_api=True)
@serialize_json()
def delete_training():
    return { "signals_deleted": TrainingNetwork().clear_training() }


@post('/option', is_api=True)
@require_fields(["key", "value"])
@serialize_json()
def post_option():
    body = request.json
    return SystemBase().set_option(body["key"], body["value"])


@get('/option', is_api=True)
@serialize_json()
def get_option():
    return SystemBase().get_options()
