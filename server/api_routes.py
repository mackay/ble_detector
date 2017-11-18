from bottle import hook
from bottle import abort
from bottle import request, post, delete, get

from core.apiutil import require_fields, serialize_json, get_configuration

from core.models import database

from core.system import SystemBase
from core.activity import DetectorActivity, BeaconActivity, AgentActivity
from core.classifier import Trainer, TrainingActivity

import pickle

import logging
log = logging.getLogger()


networks = None


def load_networks():
    networks = [ ]

    config = get_configuration()
    for network_file_source in config["networks"]:
        with open(network_file_source, 'rb') as network:
            networks.append( pickle.load(network) )

    return networks


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
    activity = DetectorActivity(body["uuid"])

    metadata = body["metadata"] if "metadata" in body else None
    return activity.checkin(metadata=metadata)


@post('/agent', is_api=True)
@require_fields(["uuid"])
@serialize_json()
def post_agent():
    body = request.json
    activity = AgentActivity(body["uuid"])

    metadata = body["metadata"] if "metadata" in body else None
    return activity.checkin(metadata=metadata)


@post('/beacon', is_api=True)
@require_fields(["uuid"])
@serialize_json()
def post_beacon():
    body = request.json
    activity = BeaconActivity(body["uuid"])

    metadata = body["metadata"] if "metadata" in body else None

    checkin_response = activity.checkin(metadata=metadata)

    if "is_accepted" in body:
        beacon = activity.get()
        beacon.is_accepted = 1 if body["is_accepted"] else 0
        beacon.save()

    return checkin_response


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

    #regardless of accepting the signal, go ahead and check in the detector
    detector_activity = DetectorActivity(body["detector_uuid"])
    detector_activity.checkin()

    becon_activity = BeaconActivity(body["beacon_uuid"])
    becon_activity.checkin()

    #if we don't fit the filter, dump the signal
    beacon_filter = SystemBase().get_option(SystemBase.FILTER_KEY)
    if beacon_filter and beacon_filter not in body["beacon_uuid"]:
        abort(409, "Signnals from beacon UUID {uuid} not acceptable to current server filter: {filter}".format(
            uuid=body["beacon_uuid"],
            filter=beacon_filter))

    if not becon_activity.get().is_accepted:
        abort(409, "Signals from beacon UUID {uuid} are not currently accepted.".format(
            uuid=body["beacon_uuid"]))

    return detector_activity.add_signal(body["beacon_uuid"], body["rssi"], source_data=source_data)


@get('/detector', is_api=True)
@serialize_json()
def get_detector():
    return DetectorActivity.get_all()


@get('/agent', is_api=True)
@serialize_json()
def get_agent():
    return AgentActivity.get_all()


@get('/beacon', is_api=True)
@serialize_json()
def get_beacon():

    stale_time_ms = None
    if request.query.stale_time_ms:
        stale_time_ms = float(request.query.stale_time_ms)
        beacons = BeaconActivity.get_active(stale_time_ms)
    else:
        beacons = BeaconActivity.get_all()

    if request.query.predict:

        #get the networks if they arent' already there
        global networks
        if networks is None:
            networks = load_networks()

        #run through all networks for all beacons
        for beacon in beacons:
            signal_slice = BeaconActivity(beacon.uuid).get_signal_slice(stale_time_ms=stale_time_ms)

            beacon._data["predict"] = { }
            for network in networks:
                beacon._data["predict"][network.dimension] = network.predict(signal_slice)

    return beacons


@post('/training', is_api=True)
@require_fields(["beacon_uuid"])
@serialize_json()
def post_training():
    #get stale seconds parameter
    stale_signal_limit = int( request.query.stale_signal_limit or str(10) )

    #if beacon is involved get it from body
    beacon_uuid = request.json["beacon_uuid"]
    expectation = request.json["expectation"] or None

    training_activity = TrainingActivity()
    training = training_activity.add(beacon_uuid, expectation=expectation, stale_signal_limit=stale_signal_limit)

    if training is None:
        abort(404, "No available (non-stale) signals for training beacon.")

    training._data["signals"] = training_activity.get_signals( training )
    training._data["normalized"] = [ ]

    normalized_signals = training_activity.normalize_signals_dbm( [ signal.rssi for signal in training._data["signals"] ] )
    for idx, signal in enumerate( training._data["signals"] ):
        training._data["normalized"].append({
            "beacon": signal._data["beacon"],
            "signal": normalized_signals[idx]
        })

    return training


@get('/training', is_api=True)
def get_training():
    return Trainer().get_training_csv()


# DELETE Resources
@delete('/training', is_api=True)
@serialize_json()
def delete_training():
    return { "deleted": Trainer.clear_training() }


@delete('/signal', is_api=True)
@serialize_json()
def delete_signal():
    return { "deleted": DetectorActivity.clear_signals() }


@delete('/detector', is_api=True)
@serialize_json()
def delete_detector():
    return { "deleted": DetectorActivity.clear_entities() }


@delete('/agent', is_api=True)
@serialize_json()
def delete_agent():
    return { "deleted": AgentActivity.clear_entities() }


@delete('/beacon', is_api=True)
@serialize_json()
def delete_beacon():
    return { "deleted": BeaconActivity.clear_entities() }
