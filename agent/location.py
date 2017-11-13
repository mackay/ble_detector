
from agent import HTTPBeaconAgent

from display import Pixel
from display.atmosphere import ExpandingSplotches

from datetime import datetime


#agent to map a discrete location strings to a color and react accordingly
class LocationAgent(HTTPBeaconAgent):

    DEFAULT_COLOR = Pixel(255, 255, 255)

    def __init__(self,
                 api_url,
                 world,
                 default_color=None,
                 location_color_map=None,
                 splotches_per_action=3,
                 refresh_max_rate_ms=250,
                 stale_time_ms=5*1000,
                 trigger_time_ms=500,
                 state={}):
        super(LocationAgent, self).__init__( api_url,
                                             refresh_max_rate_ms=refresh_max_rate_ms,
                                             stale_time_ms=stale_time_ms,
                                             trigger_time_ms=trigger_time_ms,
                                             state=state )

        self.default_color = default_color or LocationAgent.DEFAULT_COLOR
        self.location_color_map = location_color_map or { }

        self.world = world
        self.splotches_per_action = splotches_per_action

    def _get_beacon_location(self, beacon):
        if "predict" in beacon and "location" in beacon["predict"]:
            return beacon["predict"]["location"]

        return None

    def _add_splotch(self, color):
        splotch = ExpandingSplotches.generate_splotch(self.world.size, color)
        self.world.add_sprite( splotch )

    def act_on_beacon(self, beacon):
        super(LocationAgent, self).act_on_beacon(beacon)

        splotch_color = self.default_color
        location = self._get_beacon_location(beacon)

        if location and location in self.location_color_map:
            splotch_color = self.location_color_map[location]

        for i in range(0, self.splotches_per_action):
            self._add_splotch(splotch_color)
