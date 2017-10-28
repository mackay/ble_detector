
from core.models import Detector, Signal
from datetime import datetime

from core.entity import EntityAgent
from core.beacon import BeaconAgent


class DetectorAgent(EntityAgent):

    def __init__(self, uuid):
        super(DetectorAgent, self).__init__(uuid, Detector)


    def add_signal(self, beacon_uuid, rssi, source_data=None):
        self.checkin()

        beacon_agent = BeaconAgent(beacon_uuid)
        beacon = beacon_agent.checkin()

        #add to DB
        signal = Signal.create(detector=self.get(), beacon=beacon, rssi=rssi, source_data=source_data)

        #add to redis
        pass

        return signal
