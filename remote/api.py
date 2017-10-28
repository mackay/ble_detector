
import requests


class API(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def checkin_detector(self, uuid):
        url = self.base_url + "/detector"
        payload = {'uuid': uuid}

        requests.post(url, json=payload)

    def send_detector_signal(self, detector_uuid, beacon_uuid, rssi, data=None):
        url = self.base_url + "/signal"

        payload = { 'detector_uuid': detector_uuid,
                    'beacon_uuid': beacon_uuid,
                    'rssi': rssi }

        requests.post(url, json=payload)
