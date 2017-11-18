
from agent import HTTPBeaconAgent

from display import Pixel
from display.atmosphere import ExpandingSplotches
from display.sprites import Point
from display.dynamics import Lifespan


#agent to map a discrete location strings to a color and react accordingly
class LocationAgent(HTTPBeaconAgent):

    DEFAULT_COLOR = Pixel(255, 255, 255)

    STATE_SPRITE_COUNT = "sprite_count"

    def __init__(self,
                 uuid,
                 api_url,
                 world,
                 default_color=None,
                 location_color_map=None,
                 splotches_per_action=3,
                 refresh_max_rate_ms=250,
                 stale_time_ms=5*1000,
                 trigger_time_ms=500,
                 state={}):
        super(LocationAgent, self).__init__( uuid,
                                             api_url,
                                             refresh_max_rate_ms=refresh_max_rate_ms,
                                             stale_time_ms=stale_time_ms,
                                             trigger_time_ms=trigger_time_ms,
                                             state=state )

        self.default_color = default_color or LocationAgent.DEFAULT_COLOR
        self.location_color_map = location_color_map or { }

        self.world = world
        self.splotches_per_action = splotches_per_action

    def _setup(self):
        self._set_state(LocationAgent.STATE_SPRITE_COUNT, 0)

    def _get_beacon_location(self, beacon):
        if "predict" in beacon and "location" in beacon["predict"]:
            return beacon["predict"]["location"]

        return None

    def _get_beacon_color(self, beacon):
        if "metadata" in beacon and beacon["metadata"] and "color" in beacon["metadata"]:
            color = beacon["metadata"]["color"]

            #we're going to toss some alpha on top if the color doesn't have any
            #  ... this just looks better faded a bit
            if len(color) == 6:
                color += "44"

            return Pixel.from_rgb_string( color )

        return None

    def _add_splotch(self, color):
        splotch = ExpandingSplotches.generate_splotch(self.world.size, color)
        self.world.add_sprite( splotch )

        self._increment_sprite_count()

        return splotch

    def _add_point(self, position, color):
        point = Point( color=color, position=position )
        point.add_dynamic( Lifespan(life_ms=2500) )

        self.world.add_sprite(point)
        self._increment_sprite_count()

        return point

    def _increment_sprite_count(self):
        sprite_count = self._get_state(LocationAgent.STATE_SPRITE_COUNT, 0)
        sprite_count += 1
        self._set_state(LocationAgent.STATE_SPRITE_COUNT, sprite_count)

    def act_on_beacon(self, beacon):
        super(LocationAgent, self).act_on_beacon(beacon)

        splotch_color = self.default_color
        beacon_color = self._get_beacon_color(beacon)
        location = self._get_beacon_location(beacon)

        if location and location in self.location_color_map:
            splotch_color = self.location_color_map[location]

        for i in range(0, self.splotches_per_action):
            splotch = self._add_splotch(splotch_color)

            if beacon_color:
                self._add_point(splotch.position, beacon_color)
