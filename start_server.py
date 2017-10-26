#!/usr/bin/env python
import bottle
from bottle import run, static_file, route, hook
from bottle import request, post
from bottle import view

import argparse
import sys

from core.apiutil import require_fields, serialize_json

from core.models import before_request_handler, after_request_handler
from core.models import initialize

from core.detector import DetectorProcess


import logging
log = logging.getLogger()


@hook('before_request')
def before_request():
    before_request_handler()


@hook('after_request')
def after_request():
    after_request_handler()


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

@route('/')
@view('menu')
def static_index():
    return dict()


@route('/<filename:path>')
def all_static(filename):
    return static_file(filename, root='./server/static')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='store', type=str, default="localhost",
                        help='Hostname')
    parser.add_argument('--port', action='store', type=int, default=80,
                        help='Port')

    arg = parser.parse_args(sys.argv[1:])

    log.setLevel(logging.DEBUG)
    log.info("Starting Server")

    #start the WSGI app
    bottle.TEMPLATE_PATH = [ "./server/views" ]
    run(host=arg.host, port=arg.port)

    log.info("Shutdown Server")

if __name__ == "__main__":
    initialize()
    main()
