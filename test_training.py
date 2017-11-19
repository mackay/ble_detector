#!/usr/bin/env python
import argparse
import sys
import glob
import pickle

from core.classifier import Trainer
from core.models import Signal, Detector

import logging
log = logging.getLogger()


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    logging.basicConfig(format="%(thread)d:%(asctime)s:%(levelname)s:%(module)s :: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--signals', type=str,
                        help='Signals in the format of rssi,rssi,...')
    parser.add_argument('-d', '--detectors', type=str,
                        help='Detectors in the format of uuid,uuid,...')
    parser.add_argument('-v', action="store_true", dest="verbose", default=False,
                        help='Show verbose logging messages')

    parser.add_argument('-p', '--pickle', action="store_true", default=False,
                        help="Pickle networks to files as [dimension].network")

    parser.add_argument('-l', '--load', action="store_true", default=False,
                        help="Load pickled networks from files as *.network")

    arg = parser.parse_args(sys.argv[1:])

    if arg.verbose:
        log.setLevel(logging.DEBUG)

    signal_list = arg.signals.split(",")
    detector_uuid_list = arg.detectors.split(",")

    signals = [ ]
    for idx, rssi in enumerate( signal_list ):
        detector = Detector()
        detector.uuid = detector_uuid_list[idx]

        signal = Signal()
        signal.rssi = float(rssi)
        signal.detector = detector

        signals.append(signal)

    if arg.load:
        pickled_network_files = glob.glob('*.network')
        networks = [ pickle.load(open(filename, 'rb')) for filename in pickled_network_files ]
    else:
        networks = Trainer().train()

    if arg.pickle:
        for network in networks:
            pickle.dump(network, open(network.dimension + ".network", 'wb'))

    if signals:
        for network in networks:
            print network.dimension + ": " + str(network.predict(signals))
