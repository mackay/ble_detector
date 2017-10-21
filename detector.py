

class Detector(object):

    def __init__(self, uuid):
        self.uuid = uuid

    def add_signal(self, beacon_uuid, rssi, rssi_processed=None):
        rssi_processed = rssi_processed or rssi

        #add to DB

        #add to redis

    def checkin(self, status_dictionary=None):
        pass

        #if not in DB, create

        #update DB data
