
from core.models import Beacon
from core.entity import EntityAgent


class BeaconAgent(EntityAgent):

    def __init__(self, uuid):
        super(BeaconAgent, self).__init__(uuid, Beacon)
