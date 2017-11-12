
from core.models import Beacon
from core.entity import ActiveEntity


class BeaconActivity(ActiveEntity):

    EntityClass = Beacon

    def __init__(self, uuid):
        super(BeaconActivity, self).__init__(uuid)
