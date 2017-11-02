#!/usr/bin/env python
import argparse
import sys

from core.training import TrainingNetwork
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

    network = TrainingNetwork()
    network.train()

    print network.predict(signals)
