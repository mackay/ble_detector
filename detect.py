#!/usr/bin/env python

#sourced from Ian Harvey's bluepy blescan.py
#https://raw.githubusercontent.com/IanHarvey/bluepy/master/bluepy/blescan.py

from __future__ import print_function
import argparse
import binascii
import os
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


def dump_services(dev):
    services = sorted(dev.services, key=lambda s: s.hndStart)
    for s in services:
        print ("\t%04x: %s" % (s.hndStart, s))
        if s.hndStart == s.hndEnd:
            continue
        chars = s.getCharacteristics()
        for i, c in enumerate(chars):
            props = c.propertiesToString()
            h = c.getHandle()
            if 'READ' in props:
                val = c.read()
                if c.uuid == btle.AssignedNumbers.device_name:
                    string = ANSI_CYAN + '\'' + \
                        val.decode('utf-8') + '\'' + ANSI_OFF
                elif c.uuid == btle.AssignedNumbers.device_information:
                    string = repr(val)
                else:
                    string = '<s' + binascii.b2a_hex(val).decode('utf-8') + '>'
            else:
                string = ''
            print ("\t%04x:    %-59s %-12s %s" % (h, c, props, string))

            while True:
                h += 1
                if h > s.hndEnd or (i < len(chars) - 1 and h >= chars[i + 1].getHandle() - 1):
                    break
                try:
                    val = dev.readCharacteristic(h)
                    print ("\t%04x:     <%s>" %
                           (h, binascii.b2a_hex(val).decode('utf-8')))
                except btle.BTLEException:
                    break


class ScanPrint(btle.DefaultDelegate):

    def __init__(self, opts):
        btle.DefaultDelegate.__init__(self)
        self.opts = opts

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            status = "new"
        elif isNewData:
            if self.opts.new:
                return
            status = "update"
        else:
            if not self.opts.all:
                return
            status = "old"

        if dev.rssi < self.opts.sensitivity:
            return

        print ('    Device (%s): %s (%s), %d dBm %s' %
               (status,
                   ANSI_WHITE + dev.addr + ANSI_OFF,
                   dev.addrType,
                   dev.rssi,
                   ('' if dev.connectable else '(not connectable)'))
               )
        for (sdid, desc, val) in dev.getScanData():
            if sdid in [8, 9]:
                print ('\t' + desc + ': \'' + ANSI_CYAN + val + ANSI_OFF + '\'')
            else:
                print ('\t' + desc + ': <' + val + '>')
        if not dev.scanData:
            print ('\t(no data)')
        print


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

        print ( '(%s): (%d) - (%d)' % ( dev.addr, dev.rssi, self.get_computed_value(dev.addr) ) )
        print

    def add_value(self, addr, rssi):
        if addr not in self.values_map.keys():
            self.values_map[addr] = [ ]

        self.values_map[addr].append(rssi)
        self.values_map[addr] = self.values_map[addr][-1*self.opts.packets:]

    def get_computed_value(self, addr):
        avg_set = self.values_map[addr]

        if self.reject and len(avg_set) > self.packets - self.reject:
            avg_set = avg_set.sort()[(self.packets - self.reject):]

        avg = sum(avg_set) / float(len(avg_set))

        return avg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--hci', action='store', type=int, default=0,
                        help='Interface number for scan')
    parser.add_argument('-t', '--timeout', action='store', type=int, default=300,
                        help='Scan delay, 0 for continuous')
    parser.add_argument('-l', '--loops', action='store', type=int, default=1,
                        help='Scan repeat times, -1 for continuous')
    parser.add_argument('-p', '--prefix', action='store', type=str, default=None,
                        help='Filter to id prefxes of ...')
    parser.add_argument('-s', '--sensitivity', action='store', type=int, default=-128,
                        help='dBm value for filtering far devices')

    parser.add_argument('--packets', action='store', type=int, default=3,
                        help='Average RSSI values across this # of packets')
    parser.add_argument('--reject', action='store', type=int, default=0,
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
