#!/usr/bin/env python

#sourced from Ian Harvey's bluepy blescan.py
#https://raw.githubusercontent.com/IanHarvey/bluepy/master/bluepy/blescan.py
from __future__ import print_function

import argparse
import sys
import uuid
import os

from remote.scan import get_scanner, ANSI_RED, ANSI_OFF
from remote.api import API

CHECKIN_LOOPS = 10


def to_fixed_decimal(number):
    return "{0:.2f}".format( float(number))


def checkin(transport, uuid):
    load = os.getloadavg()

    for i in range(len(load)):
        load[i] = to_fixed_decimal(load[i])

    meta = {
        "load": "{0} {1} {2}".format(load)
    }

    transport.checkin_detector(uuid, metadata=meta)



def scan_loop(arg):
    transport = None
    if arg.api:
        try:
            API(arg.api).checkin_detector(arg.uuid)
            transport = API(arg.api, ignore_errors=True)
        except:
            transport = None
            print ( "Failed to access URL " + str(arg.api) + " for detector checkin.  Removing transport layer." )

    scanner = get_scanner(arg.uuid, transport=transport, interface=arg.hci, verbose=arg.verbose, opts=arg)

    loop_label = str(arg.loops) if arg.loops else "continuous"
    print (ANSI_RED + "Scanning for devices... (%s loops)" % (loop_label) + ANSI_OFF)

    checkin = CHECKIN_LOOPS

    keep_looping = True
    while keep_looping:
        scanner.scan( float(arg.timeout) / 1000 )

        if arg.loops > 0:
            arg.loops -= 1
        if arg.loops == 0:
            keep_looping = False

        checkin -= 1
        if checkin <= 0:
            checkin = CHECKIN_LOOPS
            if transport:
                checkin(transport, arg.uuid)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--hci', action='store', type=int, default=0,
                        help='Interface number for scan')
    parser.add_argument('-t', '--timeout', action='store', type=int, default=150,
                        help='Scan delay, 0 for continuous')
    parser.add_argument('-l', '--loops', action='store', type=int, default=1,
                        help='Scan repeat times, -1 for continuous')
    parser.add_argument('-p', '--prefix', action='store', type=str, default=None,
                        help='Filter to id prefxes of ...')
    parser.add_argument('-s', '--sensitivity', action='store', type=int, default=-128,
                        help='dBm value for filtering far devices')

    parser.add_argument('--packets', action='store', type=int, default=5,
                        help='Average RSSI values across this # of packets')
    parser.add_argument('--reject', action='store', type=int, default=2,
                        help='Reject # of the lowest RSSI valued packets')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity')


    parser.add_argument('--uuid', type=str, default=uuid.uuid4(),
                        help='Unique identifier for the detector')
    parser.add_argument('--api', type=str, default=None,
                        help='Base server API URL')

    arg = parser.parse_args(sys.argv[1:])

    scan_loop(arg)

if __name__ == "__main__":
    main()
