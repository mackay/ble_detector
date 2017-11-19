
from agent.location import LocationAgent
from display import Pixel


#agent to map a location from 0 ... 1 to a sequence of pixels and react accordingly
class LinearAgent1D(LocationAgent):

    DEFAULT_COLOR = Pixel(255, 255, 255)

    def __init__(self,
                 uuid,
                 api_url,
                 world,
                 default_color=None,

                 min_position=0.,
                 max_position=1.,
                 position_field="position_regression",

                 refresh_max_rate_ms=250,
                 stale_time_ms=5*1000,
                 trigger_time_ms=500,
                 state={}):
        super(LinearAgent1D, self).__init__( uuid,
                                             api_url,
                                             world,
                                             default_color=default_color,
                                             refresh_max_rate_ms=refresh_max_rate_ms,
                                             stale_time_ms=stale_time_ms,
                                             trigger_time_ms=trigger_time_ms,
                                             state=state )
        self.min_position = min_position
        self.max_position = max_position
        self.position_field = position_field

    def _get_beacon_location(self, beacon):
        pixel_position = None

        if "predict" in beacon and self.position_field in beacon["predict"]:
            real_position = float( beacon["predict"][self.position_field] )

            #we want to turn the "real" position into a floating value between 0 ... 1
            position_ratio = ( real_position - self.min_position) / ( self.max_position - self.min_position )
            position_ratio = max( 0., min(1., position_ratio) )

            #use the ratio against the world size to get where we are - make sure it is an integer
            pixel_position = int( position_ratio * self.world.size )

        return pixel_position

    def act_on_beacon(self, beacon):
        super(LocationAgent, self).act_on_beacon(beacon)

        splotch_color = self._get_beacon_color(beacon)
        location = self._get_beacon_location(beacon)

        splotch = self._add_splotch(splotch_color, position=location)

        return splotch
