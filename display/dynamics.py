from colour import Color
from scene import Dynamic

from random import randint, uniform, random


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


SHIFT_UP = 1
SHIFT_DOWN = -1
SHIFT_BOTH = None


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

    def act_on(self, sprite, world):
        super(RightDrift, self).act_on(sprite, world)

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

    def act_on(self, sprite, world):
        super(Twinkle, self).act_on(sprite, world)

        if Twinkle.TWINKLE_BASE_COLOR not in sprite.state:
            sprite.state[Twinkle.TWINKLE_BASE_COLOR] = sprite.color

        #only reset color on twinkle frequency
        if random() < self.l_shift_frequency:
            sprite.color = sprite.state[Twinkle.TWINKLE_BASE_COLOR].copy()

        #if we hit the twinkle frequency, shift the base color
        if random() < self.l_shift_frequency:
            sprite.color = l_shift_range( sprite.state[Twinkle.TWINKLE_BASE_COLOR],
                                          self.l_shift_max )
