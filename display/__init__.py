import uuid

from datetime import datetime


class Pixel(object):

    RED_INDEX = 0
    GREEN_INDEX = 1
    BLUE_INDEX = 2
    ALPHA_INDEX = 3

    @classmethod
    def from_tuple(cls, rgb_or_rgba_tuple):
        a = 255
        if len(rgb_or_rgba_tuple) > 3:
            a = rgb_or_rgba_tuple[cls.ALPHA_INDEX]

        return cls( r=rgb_or_rgba_tuple[cls.RED_INDEX],
                    g=rgb_or_rgba_tuple[cls.GREEN_INDEX],
                    b=rgb_or_rgba_tuple[cls.BLUE_INDEX],
                    a=a )

    @classmethod
    def from_tuple_n(cls, rgb_or_rgba_tuple):
        a = 1
        if len(rgb_or_rgba_tuple) > 3:
            a = rgb_or_rgba_tuple[cls.ALPHA_INDEX]

        return cls( r=rgb_or_rgba_tuple[cls.RED_INDEX]*255,
                    g=rgb_or_rgba_tuple[cls.GREEN_INDEX]*255,
                    b=rgb_or_rgba_tuple[cls.BLUE_INDEX]*255,
                    a=a*255 )

    def __init__(self, r=0, g=0, b=0, a=255):
        super(Pixel, self).__init__()
        self._components = [0] * 4
        self.set_color(r, g, b, a)

    def set_color(self, r, g, b, a=255):
        incoming = r / 255., g / 255., b / 255., a / 255.
        self._components = incoming

    def set_color_n(self, r, g, b, a=1):
        incoming = r, g, b, a
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
        return (self.r + self.g + self.b) / 255.

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

    def _blend_channel(self, incoming, background, alpha):
        if alpha == 1:
            return incoming

        if alpha == 0:
            return background

        return (incoming - background) * alpha + background

    def blend(self, other, mask=None, opacity=None, blendfunc=None):
        opacity = opacity or other.a_n

        r = self._blend_channel( other.r_n, self.r_n, opacity )
        g = self._blend_channel( other.g_n, self.g_n, opacity )
        b = self._blend_channel( other.b_n, self.b_n, opacity )

        self._components = r, g, b, self._components[Pixel.ALPHA_INDEX]

        # self.set_color_n( r, g, b, self.a_n )

        # layer = super(Pixel, self).blend(other, mask, opacity, blendfunc)
        # self.__set_color_from_layer(layer)

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


class DisplayEntity(object):
    def __init__(self):
        self.id = str(uuid.uuid4())

    def destroy(self):
        pass


class SpriteContainer(DisplayEntity):
    def __init__(self):
        super(SpriteContainer, self).__init__()
        self.sprites = [ ]

    def clear_sprites(self):
        for sprite in self.get_sprites():
            sprite.destroy()

        self.sprites = [ ]

    def add_sprite(self, sprite):
        self.sprites.append(sprite)

    def remove_sprite(self, sprite, recurse=True):
        if recurse:
            for needle in self.sprites:
                needle.remove_sprite(sprite)

        self.sprites[:] = [ needle for needle in self.sprites if needle.id != sprite.id ]

    def get_sprites(self):
        return self.sprites[:]

    def destroy(self):
        super(SpriteContainer, self).destroy()
        self.clear_sprites()


class Sprite(SpriteContainer):
    def __init__(self, position=None):
        super(Sprite, self).__init__()

        self.position = position or 0

    def render_to(self, pixel_buffer):
        for sprite in self.sprites:
            sprite.render_to(pixel_buffer)

    def is_in_buffer(self, pixel_buffer, position=None):
        if position is None:
            position = self.position

        return position >= 0 and position < len(pixel_buffer)


class DynamicSprite(Sprite):
    def __init__(self, position=None):
        super(DynamicSprite, self).__init__(position=position)

        self.state = { }
        self.dynamics = [ ]

    def add_dynamic(self, dynamic):
        self.dynamics.append(dynamic)

    def clear_dynamics(self):
        for dynamic in self.dynamics:
            dynamic.destroy()

        self.dynamics = [ ]

    def update_from(self, world, elapsed_time_ms):
        for sprite in self.sprites:
            if isinstance(sprite, DynamicSprite):
                sprite.update_from(world, elapsed_time_ms)

        for dynamic in self.dynamics:
            dynamic.act_on(self, world, elapsed_time_ms)

    def destroy(self):
        super(DynamicSprite, self).destroy()
        self.clear_dynamics()


class Dynamic(DisplayEntity):
    def __init__(self):
        super(Dynamic, self).__init__()

    def act_on(self, sprite, world, elapsed_time_ms):
        pass


class RenderableContainer(SpriteContainer):
    def __init__(self, pixel_count, fps_limit=60):
        super(RenderableContainer, self).__init__()
        self.pixels = [ Pixel() for i in range(pixel_count) ]
        self.renderers = [ ]

        self.render_last = datetime.utcnow()
        self.render_ms_limit = 1000. / float(fps_limit)

    def clear_renderers(self):
        for renderer in self.renderers:
            renderer.destroy()

        self.renderers = [ ]

    def add_renderer(self, renderer):
        renderer.setup(len(self.pixels), self)
        self.renderers.append(renderer)

    def get_renderers(self):
        return self.renderers[:]

    def render(self):
        timing_current = datetime.utcnow()
        timing_elapsed = (timing_current - self.render_last).microseconds / 1000.

        if timing_elapsed >= self.render_ms_limit:
            self.render_last = timing_current

            for sprite in self.sprites:
                sprite.render_to(self.pixels)

            for renderer in self.renderers:
                renderer.render_buffer(self.pixels)

    def destroy(self):
        super(RenderableContainer, self).destroy()
        self.clear_renderers()


class Renderer(DisplayEntity):
    def __init__(self):
        super(Renderer, self).__init__()

    def setup(self, pixel_count, world):
        pass

    def render_buffer(self, pixel_buffer):
        pass


class World(RenderableContainer):
    def __init__(self, pixel_count, print_fps=False, timing_ms_per_update=33.3):
        super(World, self).__init__(pixel_count)
        self.state = { }

        self.run_enable = True

        self.timing_previous_frame = datetime.utcnow()
        self.timing_ms_per_update = timing_ms_per_update

        self.timing_lag = 0.0
        self.timing_elapsed_ms = 0.0

        self.print_fps = print_fps

    def update(self, elapsed_time_ms):
        for sprite in self.sprites:
            sprite.update_from(self, elapsed_time_ms)

    def run(self, callback=None):
        lag = 0.0

        #do at least one update before rendering
        self.update(self.timing_elapsed_ms)

        while self.run_enable:
            timing_current = datetime.utcnow()
            timing_elapsed = (timing_current - self.timing_previous_frame).microseconds / 1000.

            if self.print_fps and timing_elapsed:
                print '{0:.2f}'.format(1000. / float(timing_elapsed)) + " fps @ " + str(timing_elapsed) + " ms / frame"

            self.timing_previous_frame = timing_current
            lag += timing_elapsed

            while lag > self.timing_ms_per_update:
                self.update( self.timing_ms_per_update )

                self.timing_elapsed_ms += self.timing_ms_per_update
                lag -= self.timing_ms_per_update

            if callback:
                callback(self)

            self.render()

    def stop(self):
        self.run_enable = False
