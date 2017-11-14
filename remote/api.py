
import requests


class API(object):

    def __init__(self, base_url, ignore_errors=False):
        self.base_url = base_url
        self.ignore_errors = ignore_errors

    def _checkin(self, resource_uri_fragment, uuid, metadata):
        url = self.base_url + resource_uri_fragment
        payload = {'uuid': uuid, 'metadata': metadata}

        try:
            requests.post(url, json=payload)
        except:
            if self.ignore_errors:
                print ("Failed to checkin to " + url)
            else:
                raise

    def checkin_detector(self, uuid, metadata=None):
        self._checkin("/detector", uuid, metadata)

    def checkin_agent(self, uuid, metadata=None):
        self._checkin("/agent", uuid, metadata)

    def send_detector_signal(self, detector_uuid, beacon_uuid, rssi, data=None):
        url = self.base_url + "/signal"

        payload = { 'detector_uuid': detector_uuid,
                    'beacon_uuid': beacon_uuid,
                    'rssi': rssi }
        try:
            requests.post(url, json=payload)
        except:
            if self.ignore_errors:
                print ("Failed to post signal to " + url)
            else:
                raise

    def get_active_beacons(self, stale_time_ms):
        url = self.base_url + "/beacon"

        params = { "stale_time_ms": stale_time_ms,
                   "predict": True }

        try:
            response = requests.get(url, params=params)
            return response.json()
        except:
            if self.ignore_errors:
                print ("Failed to get beacons")
                return [ ]
            else:
                raise
