from bottle import hook
from bottle import abort
from bottle import request, post, delete, get

from core.apiutil import require_fields, serialize_json, get_configuration

from core.models import database

from core.system import SystemBase
from core.detector import DetectorActivity
from core.beacon import BeaconActivity
from core.classifier import Network, TrainingActivity

import json
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
    detector_activity = DetectorActivity(body["uuid"])

    metadata = body["metadata"] if "metadata" in body else None
    return detector_activity.checkin(metadata=metadata)


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

    detector_activity = DetectorActivity(body["detector_uuid"])
    return detector_activity.add_signal(body["beacon_uuid"], body["rssi"], source_data=source_data)


@get('/detector', is_api=True)
@serialize_json()
def get_detector():
    return DetectorActivity.get_all()


@get('/beacon', is_api=True)
@serialize_json()
def get_beacon():

    if request.query.stale_time_ms:
        beacons = BeaconActivity.get_active(request.query.stale_time_ms)
    else:
        beacons = BeaconActivity.get_all()

    if request.query.predict:

        #get the networks if they arent' already there
        global networks
        if networks is None:
            networks = load_networks()

        #run through all networks for all beacons
        for beacon in beacons:
            beacon._data["predict"] = { }

            for network in networks:
                beacon._data["predict"][network.dimension] = network.predict_beacon(beacon)

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

    normalized_signals = training_activity.normalize_signals( [ signal.rssi for signal in training._data["signals"] ] )
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
    return { "deleted": DetectorActivity.clear_signals() }


@delete('/detector', is_api=True)
@serialize_json()
def delete_detector():
    return { "deleted": DetectorActivity.clear_entities() }


@delete('/beacon', is_api=True)
@serialize_json()
def delete_beacon():
    return { "deleted": BeaconActivity.clear_entities() }
