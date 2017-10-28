
from core.system import SystemBase
from core.beacon import BeaconAgent
from core.detector import DetectorAgent
from core.models import TrainingSignal, Detector

import json


class TrainingDetectorAgent(DetectorAgent):

    def __init__(self, uuid):
        super(TrainingDetectorAgent, self).__init__(uuid, Detector)

    def get_training_expectation(self):
        return json.loads( self.get_option(SystemBase.TRAINING_KEY) )

    def add_signal(self, beacon_uuid, rssi, expected_output=None, source_data=None):
        self.checkin()

        beacon_agent = BeaconAgent(beacon_uuid)
        beacon = beacon_agent.checkin()

        expected_output = expected_output or self.get_training_expectation()

        #add to DB
        signal = TrainingSignal.create( detector=self.get(),
                                        beacon=beacon,
                                        rssi=rssi,
                                        source_data=source_data,
                                        expected_output=expected_output)

        return signal


class TrainingNetwork(object):
    def __init__(self):
        pass

    def clear_training(self):
        return TrainingSignal.delete().execute()

    def build_network(self):
        pass
