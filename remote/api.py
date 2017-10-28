
import requests


class API(object):

    def __init__(self, base_url, ignore_errors=False):
        self.base_url = base_url
        self.ignore_errors = ignore_errors

    def checkin_detector(self, uuid, metadata=None):
        url = self.base_url + "/detector"
        payload = {'uuid': uuid, 'metadata': metadata}

        try:
            requests.post(url, json=payload)
        except:
            if self.ignore_errors:
                print ("Failed to checkin to " + url)
            else:
                raise

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
