
from display.scene import Sprite, Pixel

from random import randint, random


class Cloud(Sprite):

    @staticmethod
    def __alpha_adjust(rgba):
        red, green, blue, alpha = rgba
        alpha = alpha * 0.5
        return red, green, blue, alpha

    def __init__(self, position=0, color=None, min_radius=2, max_radius=6, movement_chance=0.5):
        super(Cloud, self).__init__(position=position)
        self.color = color or Pixel(237, 237, 237, 200)
        self.cloud_radius = randint(min_radius, max_radius)
        self.movement_chance = movement_chance * 100

    @property
    def _start_position(self):
        return self.position - self.cloud_radius

    @property
    def _end_position(self):
        return self.position + self.cloud_radius

    def is_cloud_in_frame(self, pixel_buffer):
        return Sprite._is_in_buffer(self._start_position, pixel_buffer) or Sprite._is_in_buffer(self._end_position, pixel_buffer)

    def update_from(self, world):
        super(Cloud, self).update_from(world)

        movement_gate = randint(0, 100)

        if movement_gate < self.movement_chance:
            self.position += 1

            if not self.is_cloud_in_frame(world.pixels):
                self.position = 0

    def render_to(self, pixel_buffer):
        super(Cloud, self).render_to(pixel_buffer)

        #front and end of cloud has alpha
        start_position = self.position - self.cloud_radius
        end_position = self.position + self.cloud_radius

        for i in range(start_position, end_position + 1):
            if not Sprite._is_in_buffer(i, pixel_buffer):
                continue

            opacity = 0.5 if i == start_position or i == end_position else 1
            pixel_buffer[i].blend(self.color, opacity=opacity)


class Sky(Sprite):
    def __init__(self, clouds=2, sky_pixel=None, cloud_pixel=None, world_size=None):
        super(Sky, self).__init__()

        self.sky_pixel = sky_pixel or Pixel(126, 192, 238)
        self.cloud_pixel = cloud_pixel or Pixel(237, 237, 237, 200)

        world_size = world_size or 25

        self.clouds = [ Cloud( color=self.cloud_pixel,
                               position=randint(0, world_size),
                               movement_chance=max(0.9, min(0.1, random())) ) for i in range(clouds) ]
        for cloud in self.clouds:
            self.add_sprite(cloud)

    def render_to(self, pixel_buffer):

        #paint the sky first
        for i in range(0, len(pixel_buffer)):
            pixel_buffer[i].blend(self.sky_pixel)

        #paint the clouds second
        super(Sky, self).render_to(pixel_buffer)
