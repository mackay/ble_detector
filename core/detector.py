
from core.models import Detector, Signal
from datetime import datetime

from core.entity import EntityProcess
from core.beacon import BeaconProcess


class DetectorProcess(EntityProcess):

    def __init__(self, uuid):
        super(DetectorProcess, self).__init__(uuid, Detector)


    def add_signal(self, beacon_uuid, rssi, source_data=None):
        self.checkin()

        beacon_process = BeaconProcess(beacon_uuid)
        beacon = beacon_process.checkin()

        #add to DB
        signal = Signal.create(detector=self.get(), beacon=beacon, rssi=rssi, source_data=source_data)

        #add to redis
        pass

        return signal
