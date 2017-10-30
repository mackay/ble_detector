
from core.system import SystemBase
from core.beacon import BeaconAgent
from core.models import Signal, Beacon
from core.models import Training, TrainingSignal
from datetime import datetime, timedelta

import json


class TrainingAgent(SystemBase):

    def __init__(self):
        super(SystemBase, self).__init__()

    def get_training_expectation(self):
        return json.loads( self.get_option(SystemBase.TRAINING_KEY) )

    def add(self, beacon_uuid, stale_signal_limit=5, expectation=None):

        expectation = expectation or self.get_training_expectation()

        beacon = BeaconAgent(beacon_uuid).get()
        stale_cutoff_date = datetime.utcnow() - timedelta(seconds=stale_signal_limit)

        query = ( Signal.select()
                        .join(Beacon, on=(Beacon.id == Signal.beacon))
                        .where(Beacon.uuid == beacon_uuid)
                        .group_by(Signal.beacon, Signal.detector)
                        .order_by(Signal.date) )

        #get all signals realted to the beacon younger than the stale counter
        #group them by detector
        #get the newest of each
        query = ( Signal.select()
                        .join(Beacon, on=(Beacon.id == Signal.beacon))
                        .where(Beacon.uuid == beacon_uuid)
                        .where(Signal.date > stale_cutoff_date)
                        .group_by(Signal.beacon, Signal.detector)
                        .order_by(Signal.date) )

        #if there aren't enough signals, skip
        if query.count() < 3:
            return None

        #create the training set if we have enough data
        training = Training.create( beacon=beacon, expectation=expectation )
        for signal in query:
            TrainingSignal.create(training=training, signal=signal)

        return training

    def get_signals(self, training):
        return [training_signal_link.signal for training_signal_link in training.signals]

    def normalize_signals(self, rssi_list):

        rssi_list = [ abs(rssi) for rssi in rssi_list ]

        max_rssi = float( max(rssi_list) )

        return [ float(rssi) / max_rssi for rssi in rssi_list ]


class TrainingNetwork(object):

    @classmethod
    def clear_training(cls):
        signal_removal_count = TrainingSignal.delete().execute()
        Training.delete().execute()

        return signal_removal_count

    def __init__(self):
        pass


    def build_network(self):
        pass
