import uuid

from Blit import Color

from datetime import datetime


class Pixel(Color):

    RED_INDEX = 0
    GREEN_INDEX = 1
    BLUE_INDEX = 2
    ALPHA_INDEX = 3

    def __init__(self, r=0, g=0, b=0, a=255):
        super(Pixel, self).__init__(r, g, b, a)

        self.dirty = True

    def set_color(self, r, g, b, a=255):

        incoming = r / 255., g / 255., b / 255., a / 255.

        for idx, element in enumerate(incoming):
            if self._components[idx] != element:
                self.dirty = True

        self._components = incoming

    def set_color_n(self, r, g, b, a=1):

        incoming = r, g, b, a

        for idx, element in enumerate(incoming):
            if self._components[idx] != element:
                self.dirty = True

        self._components = incoming

    @property
    def r(self):
        return self._components[Pixel.RED_INDEX] * 255.

    @property
    def g(self):
        return self._components[Pixel.GREEN_INDEX] * 255.

    @property
    def b(self):
        return self._components[Pixel.BLUE_INDEX] * 255.

    @property
    def a(self):
        return self._components[Pixel.ALPHA_INDEX] * 255.

    @property
    def w(self):
        return (self.r + self.g + self.b) / 255

    @property
    def r_n(self):
        return self._components[Pixel.RED_INDEX]

    @property
    def g_n(self):
        return self._components[Pixel.GREEN_INDEX]

    @property
    def b_n(self):
        return self._components[Pixel.BLUE_INDEX]

    @property
    def a_n(self):
        return self._components[Pixel.ALPHA_INDEX]

    @property
    def w_n(self):
        return (self.r_n + self.g_n + self.b_n) / 3.

    def copy(self):
        return Pixel(self.r, self.g, self.b, self.a)

    def blend(self, other, mask=None, opacity=1, blendfunc=None):
        layer = super(Pixel, self).blend(other, mask, opacity, blendfunc)
        self.__set_color_from_layer(layer)

    def adjust(self, adjustfunc):
        layer = super(Pixel, self).adjust(adjustfunc)
        self.__set_color_from_layer(layer)

    def __set_color_from_layer(self, layer):
        r, g, b, a = layer.rgba(1, 1)

        self.set_color( self.__transform_component(r),
                        self.__transform_component(g),
                        self.__transform_component(b),
                        self.__transform_component(a))

    def __transform_component(self, packed_value):
        return packed_value[0][0] * 255

    def __component(self, value):
        return str(value).ljust(5) + " "

    def __repr__(self):
        return self.__component(self.r) + self.__component(self.g) + self.__component(self.b) + self.__component(self.a)

    def __str__(self):
        return self.__repr__()


class SpriteContainer(object):
    def __init__(self):
        self.sprites = [ ]

    def clear_sprites(self):
        self.sprites = [ ]

    def add_sprite(self, sprite):
        self.sprites.append(sprite)

    def get_sprites(self):
        return self.sprites[:]


class World(SpriteContainer):
    def __init__(self, pixel_count):
        super(World, self).__init__()
        self.pixels = [ Pixel() for i in range(pixel_count) ]
        self.state = { }

        self.run_enable = True

        self.timing_previous_frame = datetime.utcnow()
        self.timing_lag = 0.0
        self.timing_ms_per_update = 33.33

    def update(self):
        for sprite in self.sprites:
            sprite.update_from(self)

    def render(self):
        for sprite in self.sprites:
            sprite.render_to(self.pixels)

    def run(self, world_frame_callback=None):
        lag = 0.0
        while self.run_enable:
            timing_current = datetime.utcnow()
            timing_elapsed = (timing_current - self.timing_previous_frame).microseconds / 1000

            self.timing_previous_frame = timing_current
            lag += timing_elapsed

            while lag > self.timing_ms_per_update:
                self.update()
                lag -= self.timing_ms_per_update

            if world_frame_callback:
                world_frame_callback(self)

            self.render()


class Sprite(SpriteContainer):
    def __init__(self, position=0):
        super(Sprite, self).__init__()

        self.id = str(uuid.uuid4())

        self.position = position
        self.dynamics = [ ]
        self.state = { }

    def add_dynamic(self, dynamic):
        self.dynamics.append(dynamic)

    def update_from(self, world):
        for sprite in self.sprites:
            sprite.update_from(world)

        for dynamic in self.dynamics:
            dynamic.act_on(self, world)

    def render_to(self, pixel_buffer):
        for sprite in self.sprites:
            sprite.render_to(pixel_buffer)

    def is_in_buffer(self, pixel_buffer, position=None):
        if position is None:
            position = self.position

        return position >= 0 and position < len(pixel_buffer)


class Dynamic(object):
    def __init__(self):
        pass

    def act_on(self, sprite, world):
        pass
