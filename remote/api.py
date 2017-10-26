

import requests
import json


class API(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def checkin_detector(self, uuid):
        pass

    def send_detector_signal(self, detector_uuid, signal_uuid, rssi, data=None):
        pass



#     def post_discovery(self, rssi, source_data):
#         url = self.server + "/"
# >>> payload = {'some': 'data'}

# >>> r = requests.post(url, data=json.dumps(payload))
