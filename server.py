#!/usr/bin/env python
from bottle import run, static_file, route, view

import argparse
import sys

import logging
log = logging.getLogger()


# POST /rssi

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
    main()
