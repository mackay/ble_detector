#sourced from Ian Harvey's bluepy blescan.py
#https://raw.githubusercontent.com/IanHarvey/bluepy/master/bluepy/blescan.py
from __future__ import print_function
import os

from bluepy import btle
from bunch import Bunch


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


class ScanDetectorDelegate(btle.DefaultDelegate):

    def __init__(self, uuid, transport, opts):
        btle.DefaultDelegate.__init__(self)
        self.opts = opts

        self.values_map = { }
        self.packets = opts.packets
        self.reject = opts.reject

        self.uuid = uuid
        self.transport = transport

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if self.opts.prefix and not dev.addr.startswith(self.opts.prefix):
            return
        self.add_value(dev.addr, dev.rssi)
        print ( '%s\t%d\t%d' % ( dev.addr, dev.rssi, self.get_computed_value(dev.addr) ) )

        if self.transport:
            self.transport.send_detector_signal(self.uuid, dev.addr, self.get_computed_value(dev.addr), dev.rssi)

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


def get_scanner(uuid, transport=None, interface=0, verbose=False, opts=Bunch()):
    btle.Debugging = verbose
    scanner = btle.Scanner( interface ).withDelegate( ScanDetectorDelegate(uuid, transport, opts) )
    return scanner


def run_scan(scanner, timeout):
    try:
        scanner.scan( float(timeout) / 1000 )
    except btle.BTLEException:
        print ("btle.BTLEException")
