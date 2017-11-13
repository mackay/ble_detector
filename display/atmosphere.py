
from display import DynamicSprite, Pixel
from display.sprites import Splotch, SolidEdgeSplotch
from display.dynamics import RightDrift

from display.sprites import Point
from display.dynamics import Twinkle
from display.dynamics import l_shift_range, SHIFT_UP, SHIFT_DOWN

from display.dynamics import Lifespan, AlphaLifespan
from display.dynamics import Expand, ExpandFade

from random import randint, uniform


class Cloud(Splotch):
    CLOUD_COLOR = Pixel(100, 100, 100, 200)

    @classmethod
    def generate(cls, color=None, position=None, min_radius=2, max_radius=6, min_movement=0.01, max_movement=0.33, world_size=25):

        #static shape
        color = color or Cloud.CLOUD_COLOR
        position = randint(0, world_size)
        radius = randint(min_radius, max_radius)
        cloud = cls(color, position, radius)

        #dynamic activity
        movement = uniform(min_movement, max_movement)
        cloud.add_dynamic( RightDrift(movement_chance=movement) )

        return cloud


class CloudCover(DynamicSprite):
    def __init__(self, clouds=2, cloud_color=None, world_size=25, cloud_min_radius=2, cloud_max_radius=10):
        super(CloudCover, self).__init__()
        self.cloud_color = cloud_color or Pixel(237, 237, 237, 200)

        for i in range(clouds):
            self.add_sprite(Cloud.generate(color=self.cloud_color,
                                           min_radius=cloud_min_radius,
                                           max_radius=cloud_max_radius,
                                           world_size=world_size))


class Sky(CloudCover):
    SKY_COLOR = Pixel(0, 0, 128)

    def __init__(self, clouds=2, sky_color=None, cloud_color=None, world_size=25):
        self.cloud_color = cloud_color or Cloud.CLOUD_COLOR
        self.sky_color = sky_color or Sky.SKY_COLOR

        super(Sky, self).__init__(clouds=clouds, cloud_color=cloud_color, world_size=world_size)

    def render_to(self, pixel_buffer):

        #paint the sky first
        for i in range(0, len(pixel_buffer)):
            pixel_buffer[i].blend(self.sky_color)

        #paint the clouds second
        super(Sky, self).render_to(pixel_buffer)


class Ground(DynamicSprite):

    NIGHT_COLOR = Pixel(0, 0, 0)
    DIRT_COLOR = Pixel(120, 72, 0)
    MEADOW_COLOR = Pixel(0, 92, 9)
    HILL_COLOR = Pixel(0, 123, 12)
    GRASS_COLOR = Pixel(1, 166, 17)

    def __init__(self, ground_color=None, brightness_variance=.05):
        self.ground_color = ground_color or Ground.DIRT_COLOR
        self.brightness_variance = brightness_variance

        super(Ground, self).__init__()

        self.ground_buffer = None

    def update_from(self, world, elapsed_time):
        super(Ground, self).update_from(world, elapsed_time)

        if self.ground_buffer is None or len(self.ground_buffer) != len(world.pixels):
            self.ground_buffer = [ self.ground_color ] * len(world.pixels)

            for i in range(0, len(world.pixels)):
                self.ground_buffer[i] = self.ground_color.copy()

                picker = randint(0, 10)
                if picker < 2:
                    self.ground_buffer[i] = l_shift_range( self.ground_buffer[i],
                                                           self.brightness_variance,
                                                           SHIFT_UP )
                elif picker > 7:
                    self.ground_buffer[i] = l_shift_range( self.ground_buffer[i],
                                                           self.brightness_variance,
                                                           SHIFT_DOWN )

    def render_to(self, pixel_buffer):

        for i in range(0, len(pixel_buffer)):
            pixel_buffer[i].blend( self.ground_buffer[i] )

        super(Ground, self).render_to(pixel_buffer)


class Star(Point):

    # Stellar types

        # O5(V)       157 180 255   #9db4ff
        # B1(V)       162 185 255   #a2b9ff
        # B3(V)       167 188 255   #a7bcff
        # B5(V)       170 191 255   #aabfff
        # B8(V)       175 195 255   #afc3ff
        # A1(V)       186 204 255   #baccff
        # A3(V)       192 209 255   #c0d1ff
        # A5(V)       202 216 255   #cad8ff
        # F0(V)       228 232 255   #e4e8ff
        # F2(V)       237 238 255   #edeeff
        # F5(V)       251 248 255   #fbf8ff
        # F8(V)       255 249 249   #fff9f9
        # G2(V)       255 245 236   #fff5ec
        # G5(V)       255 244 232   #fff4e8
        # G8(V)       255 241 223   #fff1df
        # K0(V)       255 235 209   #ffebd1
        # K4(V)       255 215 174   #ffd7ae
        # K7(V)       255 198 144   #ffc690
        # M2(V)       255 190 127   #ffbe7f
        # M4(V)       255 187 123   #ffbb7b
        # M6(V)       255 187 123   #ffbb7b

    STAR_COLORS = [
        [ 157, 180, 255 ],
        [ 162, 185, 255 ],
        [ 167, 188, 255 ],
        [ 170, 191, 255 ],
        [ 175, 195, 255 ],
        [ 186, 204, 255 ],
        [ 192, 209, 255 ],
        [ 202, 216, 255 ],
        [ 228, 232, 255 ],
        [ 237, 238, 255 ],
        [ 251, 248, 255 ],
        [ 255, 249, 249 ],
        [ 255, 245, 236 ],
        [ 255, 244, 232 ],
        [ 255, 241, 223 ],
        [ 255, 235, 209 ],
        [ 255, 215, 174 ],
        [ 255, 198, 144 ],
        [ 255, 190, 127 ],
        [ 255, 187, 123 ],
        [ 255, 187, 123 ]
    ]

    @classmethod
    def generate(cls, color=None, position=None, max_l_shift=0.3, min_movement=0.01, max_movement=0.05, world_size=25):
        #static shape
        color = color or cls.get_color()
        position = randint(0, world_size)
        star = cls(color, position)

        #dynamic activity
        movement = uniform(min_movement, max_movement)
        star.add_dynamic( RightDrift(movement_chance=movement) )
        star.add_dynamic( Twinkle(max_l_shift=max_l_shift) )

        return star

    @classmethod
    def get_color(cls):
        star_index = randint(0, len(cls.STAR_COLORS)-1)
        color = cls.STAR_COLORS[ star_index ]

        return Pixel(color[0], color[1], color[2])


class Stars(DynamicSprite):

    def __init__(self, stars=5, world_size=25):
        super(Stars, self).__init__()

        for i in range(stars):
            self.add_sprite(Star.generate(world_size=world_size))


class Raindrop(Splotch):

    RAIN_COLORS = [
        [ 0, 18, 109 ],
        [ 161, 219, 236 ],
        [ 12, 194, 221 ],
        [ 48, 146, 206 ],
        [ 0, 83, 146 ]
    ]

    @classmethod
    def generate(cls, color=None, position=None, radius=None, min_radius=0, max_radius=3, world_size=25):

        #static shape
        color = color or cls.get_color()
        position = position or randint(0, world_size)
        radius = radius or randint(min_radius, max_radius)
        drop = cls(color, position, radius)

        #dynamic activity
        drop.add_dynamic( AlphaLifespan(random_shift_ms=3000) )
        drop.add_dynamic( Expand(maximum_radius=7, expansion_rate_ms=150) )

        return drop

    @classmethod
    def get_color(cls):
        index = randint(0, len(cls.RAIN_COLORS)-1)
        color = cls.RAIN_COLORS[ index ]

        return Pixel(color[0], color[1], color[2], 128)


class Rain(DynamicSprite):

    def __init__(self, max_drops=10, drop_rate=.10, world_size=25):
        super(Rain, self).__init__()

        self.max_drops = 10
        self.drop_rate = drop_rate
        self.world_size = world_size

    def update_from(self, world, elapsed_time):
        super(Rain, self).update_from(world, elapsed_time)

        if uniform(0, 1) < self.drop_rate:
            self.add_drop()
            self.enforce_max_drops()

    def add_drop(self):
        drop = Raindrop.generate(world_size=self.world_size)
        self.add_sprite( drop )

    def enforce_max_drops(self):
        while len(self.get_sprites()) > self.max_drops:
            to_remove = self.get_sprites()[0]

            self.remove_sprite(to_remove)
            to_remove.destroy()


class ExpandingSplotches(DynamicSprite):
    def __init__(self, splotches=5):
        super(ExpandingSplotches, self).__init__()
        self.splotch_count = splotches

    def update_from(self, world, elapsed_time):
        super(ExpandingSplotches, self).update_from(world, elapsed_time)

        while len(self.get_sprites()) < self.splotch_count:
            self.add_sprite( ExpandingSplotches.generate_splotch(len(world.pixels)) )

    @classmethod
    def generate_splotch(cls, world_size, color=None):
        COLORS = [
            [ 255, 0, 0 ],
            [ 0, 255, 0 ],
            [ 0, 0, 255 ]
        ]

        color = color or Pixel.from_tuple( COLORS[ randint(0, len(COLORS)-1) ] )
        position = randint(0, world_size)
        radius = randint(0, 2)
        splotch = SolidEdgeSplotch(color, position, radius)

        #dynamic activity
        splotch.add_dynamic( ExpandFade(maximum_radius=10, expansion_rate_ms=200, destroy_on_max=True) )

        return splotch
