
from core.models import Beacon
from core.entity import EntityProcess


class BeaconProcess(EntityProcess):

    def __init__(self, uuid):
        super(BeaconProcess, self).__init__(uuid, Beacon)
