#!/usr/bin/env python

#sourced from Ian Harvey's bluepy blescan.py
#https://raw.githubusercontent.com/IanHarvey/bluepy/master/bluepy/blescan.py
from __future__ import print_function
import os

import argparse
import sys
from bluepy import btle

if os.getenv('C', '1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_OFF = ANSI_CSI + '0m'



class ScanDetector(btle.DefaultDelegate):

    def __init__(self, opts):
        btle.DefaultDelegate.__init__(self)
        self.opts = opts

        self.values_map = { }
        self.packets = opts.packets
        self.reject = opts.reject

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if self.opts.prefix and not dev.addr.startswith(self.opts.prefix):
            return
        self.add_value(dev.addr, dev.rssi)
        print ( '%s\t%d\t%d' % ( dev.addr, dev.rssi, self.get_computed_value(dev.addr) ) )

    def add_value(self, addr, rssi):
        if addr not in self.values_map.keys():
            self.values_map[addr] = [ ]

        self.values_map[addr].append(rssi)
        self.values_map[addr] = self.values_map[addr][-1*self.opts.packets:]

    def get_computed_value(self, addr):
        if addr not in self.values_map.keys():
            self.values_map[addr] = [ ]

        avg_set = self.values_map[addr][:]

        if avg_set:
            if self.reject and len(avg_set) > ( self.packets - self.reject ):
                avg_set.sort()
                avg_set = avg_set[(self.packets - self.reject):]

            avg = sum(avg_set) / float(len(avg_set))

            return avg

        return -128


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
    arg = parser.parse_args(sys.argv[1:])

    btle.Debugging = arg.verbose

    scanner = btle.Scanner(arg.hci).withDelegate(ScanDetector(arg))

    loop_label = str(arg.loops) if arg.loops else "continuous"

    print (ANSI_RED + "Scanning for devices... (%s loops)" % (loop_label) + ANSI_OFF)

    keep_looping = True
    while keep_looping:
        scanner.scan( float(arg.timeout) / 1000 )

        if arg.loops > 0:
            arg.loops -= 1
        if arg.loops == 0:
            keep_looping = False

if __name__ == "__main__":
    main()
