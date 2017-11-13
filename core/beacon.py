
from core.models import Beacon
from core.entity import ActiveEntity


class BeaconActivity(ActiveEntity):

    EntityClass = Beacon

    def __init__(self, uuid):
        super(BeaconActivity, self).__init__(uuid)

    @classmethod
    def get_active(cls, stale_time_ms):
        return [ entity for entity in cls.EntityClass.select() ]

    def get_location(self, networks):
        return { }

    def get_signal_slice(self, stale_time_ms=None):
        return [ ]
