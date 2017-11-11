
from display import Sprite, Pixel
from display.statics import Splotch
from display.dynamics import RightDrift

from display.statics import Point
from display.dynamics import Twinkle
from display.dynamics import l_shift_range, SHIFT_UP, SHIFT_DOWN

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


class CloudCover(Sprite):
    def __init__(self, clouds=2, cloud_color=None, world_size=25):
        super(CloudCover, self).__init__()
        self.cloud_color = cloud_color or Pixel(237, 237, 237, 200)

        for i in range(clouds):
            self.add_sprite(Cloud.generate(color=self.cloud_color, world_size=world_size))


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


class Ground(Sprite):

    DIRT_COLOR = Pixel(120, 72, 0)
    MEADOW_COLOR = Pixel(0, 92, 9)
    HILL_COLOR = Pixel(0, 123, 12)
    GRASS_COLOR = Pixel(1, 166, 17)

    def __init__(self, ground_color=None, brightness_variance=.05):
        self.ground_color = ground_color or Ground.DIRT_COLOR
        self.brightness_variance = brightness_variance

        super(Ground, self).__init__()

        self.ground_buffer = None

    def update_from(self, world):
        super(Ground, self).update_from(world)

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


class Stars(Ground):
    NIGHT_COLOR = Pixel(0, 0, 0)

    def __init__(self, stars=5, brightness_variance=.0, world_size=25):
        super(Stars, self).__init__(ground_color=Stars.NIGHT_COLOR, brightness_variance=brightness_variance)

        for i in range(stars):
            self.add_sprite(Star.generate(world_size=world_size))
