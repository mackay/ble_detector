#!/usr/bin/env python
import argparse
import sys

import logging
log = logging.getLogger()

from display.virtual import PyGameScene
from display.atmosphere import Sky


def world_callback(world):
    return False

PIXELS = 90


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    logging.basicConfig(format="%(thread)d:%(asctime)s:%(levelname)s:%(module)s :: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action="store_true", dest="virtual", default=False,
                        help='Use virtual scene instead of NeoPixel')

    arg = parser.parse_args(sys.argv[1:])

    try:
        from display.neopixel import NeoPixelScene
    except:
        print "Failed to load NeoPixelScene, forcing virtual"
        arg.virtual = True

    if arg.virtual:
        scene = PyGameScene(PIXELS, pixel_size=10)
    else:
        scene = NeoPixelScene(PIXELS)

    scene.add_sprite( Sky(clouds=2, world_size=PIXELS) )
    scene.run( world_callback )
