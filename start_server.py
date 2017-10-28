#!/usr/bin/env python
import bottle
from bottle import run, app, route

import argparse
import sys

from core.models import initialize

from server.site_routes import *
from server.api_routes import *

import logging
log = logging.getLogger()



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='store', type=str, default="localhost",
                        help='Hostname')
    parser.add_argument('--port', action='store', type=int, default=80,
                        help='Port')

    arg = parser.parse_args(sys.argv[1:])

    log.setLevel(logging.DEBUG)
    logging.basicConfig(format="%(thread)d:%(asctime)s:%(levelname)s:%(module)s :: %(message)s")

    log.info("Starting Server")
    log.info("Log 'general' initialized at level {0}".format( log.getEffectiveLevel() ))

    p_logger = logging.getLogger('peewee')
    p_logger.setLevel(logging.INFO)
    p_logger.info("Log 'peewee' initialized at level {0}".format( p_logger.getEffectiveLevel() ))

    pool_log = logging.getLogger("peewee.pool")
    pool_log.setLevel(logging.DEBUG)
    pool_log.info("Log 'peewee.pool' initialized at level {0}".format( pool_log.getEffectiveLevel() ))

    #print the routes and adjust routing if necessary
    for existing_route in app().routes:
        if existing_route.config.is_api:
            route("/api" + existing_route.rule, method=existing_route.method, callback=existing_route.call)
        else:
            log.info( existing_route.method + "\t" + existing_route.rule )


    #start the WSGI app
    bottle.TEMPLATE_PATH = [ "./server/views" ]
    run(host=arg.host, port=arg.port)

    log.info("Shutdown Server")

if __name__ == "__main__":
    initialize()
    main()
