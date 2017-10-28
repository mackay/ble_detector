
from core.models import Detector, Signal

from core.entity import EntityAgent
from core.beacon import BeaconAgent


class DetectorAgent(EntityAgent):

    EntityClass = Detector

    def __init__(self, uuid):
        super(DetectorAgent, self).__init__(uuid)

    def add_signal(self, beacon_uuid, rssi, source_data=None):
        self.checkin()
        self.increment_packet_count()

        beacon_agent = BeaconAgent(beacon_uuid)
        beacon = beacon_agent.checkin()
        beacon_agent.increment_packet_count()

        #add to DB
        signal = Signal.create(detector=self.get(), beacon=beacon, rssi=rssi, source_data=source_data)

        #add to redis
        pass

        return signal

    def clear_signals(self):
        return Signal.delete().execute()
