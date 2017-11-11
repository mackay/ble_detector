#!/usr/bin/env python
import argparse
import sys

import logging
log = logging.getLogger()

from display.atmosphere import Sky, Stars, Ground


def world_callback(world):
    return False

PIXELS = 90


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    logging.basicConfig(format="%(thread)d:%(asctime)s:%(levelname)s:%(module)s :: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action="store_true", dest="virtual", default=False,
                        help='Use virtual display instead of NeoPixel')

    parser.add_argument('scene', choices=["sky", "stars", "grass", "dirt"],
                        help='Which testing scene would you like?  sky, stars, grass')


    args = parser.parse_args(sys.argv[1:])

    if args.virtual:
        from display.virtual import PyGameScene
        scene = PyGameScene(PIXELS, pixel_size=10)
    else:
        from display.led import NeoPixelScene
        scene = NeoPixelScene(PIXELS)

    if args.scene == "sky":
        scene.add_sprite( Sky(clouds=2, world_size=PIXELS) )

    if args.scene == "stars":
        scene.add_sprite( Stars(stars=5, world_size=PIXELS) )

    if args.scene == "grass":
        scene.add_sprite( Ground(ground_color=Ground.MEADOW_COLOR, brightness_variance=0.10) )

    if args.scene == "dirt":
        scene.add_sprite( Ground(ground_color=Ground.DIRT_COLOR, brightness_variance=0.05) )


    scene.run( world_callback )
