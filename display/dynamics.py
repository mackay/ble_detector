from colour import Color
from scene import Dynamic

from random import randint, uniform, random


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
            base_color = sprite.state[Twinkle.TWINKLE_BASE_COLOR].copy()
            shift_color = Color(rgb=( base_color.r_n,
                                      base_color.g_n,
                                      base_color.b_n ))
            shift_color.luminance = max( 0.0, min( 1.0, uniform(shift_color.luminance - self.l_shift_max,
                                                                shift_color.luminance + self.l_shift_max) ) )

            sprite.color.set_color_n(shift_color.red,
                                     shift_color.green,
                                     shift_color.blue,
                                     sprite.color.a_n )
