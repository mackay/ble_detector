#!/usr/bin/env python
from bottle import run, static_file, route, view
from bottle import hook
from bottle import request, post

import argparse
import sys

from apiutil import require_fields

from models import before_request_handler, after_request_handler
from models import initialize

from detector import Detector


import logging
log = logging.getLogger()


# POST /detector
@post('/detector')
@require_fields(["uuid", "status_dictionary"])
def post_detector():
    body = request.json
    detector = Detector(body["uuid"])
    return detector.checkin(status_dictionary=body["status_dictionary"])


# POST /rssi
@post('/signal')
@require_fields(["detector_uuid", "beacon_uuid", "rssi"])
def post_signal():
    body = request.json

    rssi_processed = body["rssi_processed"] if "rssi_processed" in body else None

    detector = Detector(body["detector"])
    return detector.add_signal(body["beacon_uuid"], body["rssi"], rssi_processed=rssi_processed)


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
    return static_file(filename, root='./static')


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
    run(host=arg.host, port=arg.port)

    log.info("Shutdown Server")

if __name__ == "__main__":
    initialize()
    main()
