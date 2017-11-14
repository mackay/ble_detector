
from core.models import Detector, Beacon, Agent
from core.models import Signal

from core.entity import ActiveEntity

from datetime import datetime, timedelta


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


class BeaconActivity(ActiveEntity):

    EntityClass = Beacon

    def __init__(self, uuid):
        super(BeaconActivity, self).__init__(uuid)

    @classmethod
    def get_active(cls, stale_time_ms):

        cutoff = datetime.utcnow() - timedelta(milliseconds=stale_time_ms)
        return [ beacon for beacon in ( Beacon.select()
                                              .join(Signal, on=(Signal.beacon == Beacon.id))
                                              .where(Signal.date > cutoff)
                                              .group_by(Beacon.id) ) ]

    def get_prediction(self, networks, stale_time_ms=None):
        prediction = { }

        signal_slice = self.get_signal_slice(stale_time_ms=stale_time_ms)

        for network in networks:
            prediction[network.dimension] = network.predict(signal_slice)

        return prediction

    def get_signal_slice(self, stale_time_ms=None):

        # get all signals realted to the beacon
        # group them by detector
        # get the newest of each
        query = ( Signal.select()
                        .join(Beacon, on=(Beacon.id == Signal.beacon))
                        .where(Beacon.uuid == self.uuid)
                        .group_by(Signal.beacon, Signal.detector)
                        .order_by(Signal.date) )

        # ... younger than the stale counter
        if stale_time_ms:
            cutoff = datetime.utcnow() - timedelta(milliseconds=stale_time_ms)
            query = query.where(Signal.date > cutoff)

        return [ signal for signal in query ]


class AgentActivity(ActiveEntity):

    EntityClass = Agent

    def __init__(self, uuid):
        super(AgentActivity, self).__init__(uuid)
