
from random import randint, uniform, random

from colour import Color
from display import Dynamic


SHIFT_UP = 1
SHIFT_DOWN = -1
SHIFT_BOTH = None


def l_shift(pixel, shift_amount):
    shift_color = Color(rgb=( pixel.r_n,
                              pixel.g_n,
                              pixel.b_n ))

    shift_color.luminance += shift_amount

    shifted_pixel = pixel.copy()
    shifted_pixel.set_color_n( shift_color.red,
                               shift_color.green,
                               shift_color.blue,
                               pixel.a_n )
    return shifted_pixel


def l_shift_range(pixel, shift_range, direction=None):
    shift_color = Color(rgb=( pixel.r_n,
                              pixel.g_n,
                              pixel.b_n ))

    upper_bound = shift_color.luminance
    lower_bound = shift_color.luminance

    if direction is None or direction > 0:
        upper_bound += shift_range

    if direction is None or direction < 0:
        lower_bound -= shift_range

    shift_color.luminance = max( 0.0, min( 1.0, uniform( upper_bound, lower_bound ) ) )

    shifted_pixel = pixel.copy()
    shifted_pixel.set_color_n( shift_color.red,
                               shift_color.green,
                               shift_color.blue,
                               pixel.a_n )
    return shifted_pixel


class RightDrift(Dynamic):
    def __init__(self, movement_chance=0.2):
        super(RightDrift, self).__init__()

        self.movement_chance = movement_chance * 100

    def act_on(self, sprite, world, elapsed_time):
        super(RightDrift, self).act_on(sprite, world, elapsed_time)

        movement_gate = randint(0, 100)

        if movement_gate < self.movement_chance:
            sprite.position += 1

            if not sprite.is_in_buffer(world.pixels):
                sprite.position = 0


class Twinkle(Dynamic):
    TWINKLE_BASE_COLOR = "twinkle_base"

    def __init__(self, max_l_shift=0.2, frequency=0.1):
        super(Twinkle, self).__init__()
        self.l_shift_max = max(min(1.0, max_l_shift), 0.0)
        self.l_shift_frequency = frequency

    def act_on(self, sprite, world, elapsed_time):
        super(Twinkle, self).act_on(sprite, world, elapsed_time)

        if Twinkle.TWINKLE_BASE_COLOR not in sprite.state:
            sprite.state[Twinkle.TWINKLE_BASE_COLOR] = sprite.color

        #only reset color on twinkle frequency
        if random() < self.l_shift_frequency:
            sprite.color = sprite.state[Twinkle.TWINKLE_BASE_COLOR].copy()

        #if we hit the twinkle frequency, shift the base color
        if random() < self.l_shift_frequency:
            sprite.color = l_shift_range( sprite.state[Twinkle.TWINKLE_BASE_COLOR],
                                          self.l_shift_max )


class Expand(Dynamic):
    def __init__(self, expansion_rate_ms=100, maximum_radius=10, radius_adjust_fn=None, destroy_on_max=False):
        super(Expand, self).__init__()

        self.life_ms = 0
        self.rate_ms = expansion_rate_ms
        self.maximum_radius = maximum_radius

        self.radius_adjust_fn = Expand.__radius_adjust_fn
        self.destroy_on_max = destroy_on_max

    @staticmethod
    def __radius_adjust_fn(sprite, to_radius=None):
        if to_radius:
            sprite.radius = to_radius

        return sprite.radius

    def act_on(self, sprite, world, elapsed_time_ms):
        super(Expand, self).act_on(sprite, world, elapsed_time_ms)

        self.life_ms += elapsed_time_ms
        while self.life_ms > self.rate_ms:
            self.life_ms -= self.rate_ms

            radius = self.radius_adjust_fn(sprite)
            if radius < self.maximum_radius:
                radius += 1
                self.radius_adjust_fn(sprite, radius)
            elif self.destroy_on_max:
                world.remove_sprite(sprite)
                sprite.destroy()


class ExpandFade(Expand):
    def __init__(self, expansion_rate_ms=100, maximum_radius=10, radius_adjust_fn=None, destroy_on_max=False):
        super(ExpandFade, self).__init__( expansion_rate_ms=expansion_rate_ms,
                                          maximum_radius=maximum_radius,
                                          radius_adjust_fn=radius_adjust_fn,
                                          destroy_on_max=destroy_on_max)

        self.starting_radius = None

    def act_on(self, sprite, world, elapsed_time_ms):
        if self.starting_radius is None:
            self.starting_radius = self.radius_adjust_fn(sprite)

        super(ExpandFade, self).act_on(sprite, world, elapsed_time_ms)

        radius = self.radius_adjust_fn(sprite)

        # print str(self.starting_radius) + " ... " + str(radius) + " ... " + str(self.maximum_radius)
        # print ( float(radius - self.starting_radius) )
        # print ( float(self.starting_radius - self.maximum_radius) )
        # print ( float(radius - self.starting_radius) ) / ( float(self.starting_radius - self.maximum_radius) )

        alpha = 1 - ( float(radius - self.starting_radius) ) / ( float(self.maximum_radius - self.starting_radius) )

        sprite.color.set_color_n( sprite.color.r_n,
                                  sprite.color.g_n,
                                  sprite.color.b_n,
                                  alpha )


class Lifespan(Dynamic):
    def __init__(self, life_ms=5000, random_shift_ms=0):
        super(Lifespan, self).__init__()

        self.ttl_ms = life_ms + randint(-1*random_shift_ms, random_shift_ms)
        self.life_ms = 0

    def act_on(self, sprite, world, elapsed_time_ms):
        super(Lifespan, self).act_on(sprite, world, elapsed_time_ms)

        self.life_ms += elapsed_time_ms
        if self.life_ms > self.ttl_ms:
            world.remove_sprite(sprite)
            sprite.destroy()


class AlphaLifespan(Lifespan):

    def act_on(self, sprite, world, elapsed_time_ms):
        super(AlphaLifespan, self).act_on(sprite, world, elapsed_time_ms)

        self.life_ms += elapsed_time_ms
        if self.life_ms > self.ttl_ms:
            world.remove_sprite(sprite)
            sprite.destroy()
        else:
            sprite.color.set_color_n( sprite.color.r_n,
                                      sprite.color.g_n,
                                      sprite.color.b_n,
                                      1 - float(self.life_ms) / float(self.ttl_ms) )
