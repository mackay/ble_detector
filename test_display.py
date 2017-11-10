
from display.virtual import PyGameScene
from display.atmosphere import Sky

import time


def delay(world):
    time.sleep(0.5)

PIXELS = 90

scene = PyGameScene(PIXELS, pixel_size=10)
scene.add_sprite( Sky(clouds=2, world_size=PIXELS) )
scene.run( delay )
