

import requests
import json


class API(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def checkin_detector(self, uuid):
        url = self.base_url + "/detector"
        payload = {'uuid': uuid}

        requests.post(url, data=json.dumps(payload))

    def send_detector_signal(self, detector_uuid, signal_uuid, rssi, data=None):
        url = self.base_url + "/signal"

        payload = { 'detector_uuid': detector_uuid,
                    'signal_uuid': signal_uuid,
                    'rssi': rssi }

        requests.post(url, data=json.dumps(payload))
