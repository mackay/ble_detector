from bottle import hook
from bottle import abort
from bottle import request, post, delete, get

from core.apiutil import require_fields, serialize_json

from core.models import database

from core.system import SystemBase
from core.detector import DetectorAgent
from core.beacon import BeaconAgent
from core.training import TrainingNetwork, TrainingAgent

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

    metadata = body["metadata"] if "metadata" in body else None
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


@post('/training', is_api=True)
@require_fields(["beacon_uuid"])
@serialize_json()
def post_training():
    #get stale seconds parameter
    stale_signal_limit = int( request.query.stale_signal_limit or str(10) )

    #if beacon is involved get it from body
    beacon_uuid = request.json["beacon_uuid"]
    expectation = request.json["expectation"] or None

    training_agent = TrainingAgent()
    training = training_agent.add(beacon_uuid, expectation=expectation, stale_signal_limit=stale_signal_limit)

    if training is None:
        abort(404, "No available (non-stale) signals for training beacon.")

    training._data["signals"] = training_agent.get_signals( training )
    training._data["normalized"] = [ ]

    normalized_signals = training_agent.normalize_signals( [ signal.rssi for signal in training._data["signals"] ] )
    for idx, signal in enumerate( training._data["signals"] ):
        training._data["normalized"].append({
            "beacon": signal._data["beacon"],
            "signal": normalized_signals[idx]
        })

    return training


@get('/training', is_api=True)
def get_training():
    return TrainingNetwork().get_training_csv()


# DELETE Resources
@delete('/training', is_api=True)
@serialize_json()
def delete_training():
    return { "deleted": TrainingNetwork.clear_training() }


@delete('/signal', is_api=True)
@serialize_json()
def delete_signal():
    return { "deleted": DetectorAgent.clear_signals() }


@delete('/detector', is_api=True)
@serialize_json()
def delete_detector():
    return { "deleted": DetectorAgent.clear_entities() }


@delete('/beacon', is_api=True)
@serialize_json()
def delete_beacon():
    return { "deleted": BeaconAgent.clear_entities() }
