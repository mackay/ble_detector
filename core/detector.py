
from core.models import Detector, Signal

from core.entity import ActiveEntity
from core.beacon import BeaconActivity


class DetectorActivity(ActiveEntity):

    EntityClass = Detector

    @classmethod
    def clear_signals(cls):
        return Signal.delete().execute()

    def __init__(self, uuid):
        super(DetectorActivity, self).__init__(uuid)

    def add_signal(self, beacon_uuid, rssi, source_data=None):
        self.checkin()
        self.increment_packet_count()

        beacon_activity = BeaconActivity(beacon_uuid)
        beacon = beacon_activity.checkin()
        beacon_activity.increment_packet_count()

        #add to DB
        signal = Signal.create(detector=self.get(), beacon=beacon, rssi=rssi, source_data=source_data)

        #add to redis
        pass

        return signal
