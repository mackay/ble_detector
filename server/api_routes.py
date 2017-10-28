from bottle import hook
from bottle import abort
from bottle import request, post, delete, get

from core.apiutil import require_fields, serialize_json

from core.models import database

from core.system import SystemBase
from core.detector import DetectorAgent
from core.beacon import BeaconAgent
from core.training import TrainingNetwork, TrainingDetectorAgent

import json

import logging
log = logging.getLogger()


@hook('before_request')
def before_request():
    database.connect()


@hook('after_request')
def after_request():
    database.close()



# System configuration
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


# detectors and detector signals
@post('/detector', is_api=True)
@require_fields(["uuid"])
@serialize_json()
def post_detector():
    body = request.json
    detector_agent = DetectorAgent(body["uuid"])

    metadata = None
    if "metadata" in body:
        try:
            metadata = json.reads(body["metadata"])
        except:
            log.error( "Failed to parse JSON metadata " + str(body["metadata"]) )
            metadata = None

    return detector_agent.checkin(metadata=metadata)


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


@get('/detector', is_api=True)
@serialize_json()
def get_detector():
    return DetectorAgent.get_all()


@get('/beacon', is_api=True)
@serialize_json()
def get_beacon():
    return BeaconAgent.get_all()


# DELETE Resources
@delete('/training', is_api=True)
@serialize_json()
def delete_training():
    return { "deleted": TrainingNetwork().clear_training() }


@delete('/signal', is_api=True)
@serialize_json()
def delete_signal():
    return { "deleted": DetectorAgent(None).clear_signals() }


@delete('/detector', is_api=True)
@serialize_json()
def delete_detector():
    return { "deleted": DetectorAgent(None).clear_entities() }


@delete('/beacon', is_api=True)
@serialize_json()
def delete_beacon():
    return { "deleted": BeaconAgent(None).clear_entities() }
