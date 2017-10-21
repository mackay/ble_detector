#!/usr/bin/env python
from bottle import run, static_file, route, view
from bottle import hook
from bottle import request, post

import argparse
import sys

from models import before_request_handler, after_request_handler
from models import initialize

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
def post_detector():
    body = request.json


# POST /rssi
@post('/signal')
def post_signal():
    body = request.json


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
