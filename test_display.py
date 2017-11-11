#!/usr/bin/env python
import argparse
import sys

import logging
log = logging.getLogger()

from display import World
from display.atmosphere import Sky, Stars, Ground, Rain, CloudCover

import signal


def world_callback(world):
    return False

PIXELS = 90


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    logging.basicConfig(format="%(thread)d:%(asctime)s:%(levelname)s:%(module)s :: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument('--virtual', action="store_true", dest="virtual", default=False,
                        help='Use virtual display')
    parser.add_argument('--led', action="store_true", dest="led", default=False,
                        help='Use led display')
    parser.add_argument('--text-color', action="store_true", dest="text_color", default=False,
                        help='Use ansi color text display')
    parser.add_argument('--text', action="store_true", dest="text", default=False,
                        help='Use text display')

    parser.add_argument('--fps', action="store_true", dest="fps", default=False,
                        help='Show FPS')
    parser.add_argument('--profiler', action="store_true", dest="profiler", default=False,
                        help='Run timing profiler')

    parser.add_argument('scene', default="grass,clouds", nargs='?',
                        help='Which scenes to composite.  Choices include: sky, grass, dirt, night, rain, clouds, stars')


    args = parser.parse_args(sys.argv[1:])

    scene = World(PIXELS, print_fps=args.fps)

    if args.virtual:
        from display.renderers.virtual import PyGameRenderer
        scene.add_renderer( PyGameRenderer() )
    if args.led:
        from display.renderers.led import NeoPixelRenderer
        scene.add_renderer( NeoPixelRenderer() )
    if args.text_color:
        from display.renderers.text import ConsoleColorRenderer
        scene.add_renderer( ConsoleColorRenderer(clear_on_render=True) )
    if args.text:
        from display.renderers.text import ConsoleRenderer
        scene.add_renderer( ConsoleRenderer(clear_on_render=True) )


    if "sky" in args.scene:
        scene.add_sprite( Sky(clouds=2, world_size=PIXELS) )

    if "grass" in args.scene:
        scene.add_sprite( Ground(ground_color=Ground.MEADOW_COLOR, brightness_variance=0.10) )

    if "dirt" in args.scene:
        scene.add_sprite( Ground(ground_color=Ground.DIRT_COLOR, brightness_variance=0.05) )

    if "night" in args.scene:
        scene.add_sprite( Ground(ground_color=Ground.NIGHT_COLOR, brightness_variance=0.01) )

    if "rain" in args.scene:
        scene.add_sprite( Rain(max_drops=10, drop_rate=.3, world_size=PIXELS) )

    if "clouds" in args.scene:
        scene.add_sprite( CloudCover(clouds=2, world_size=PIXELS, cloud_min_radius=2, cloud_max_radius=int(PIXELS*0.2)) )

    if "stars" in args.scene:
        scene.add_sprite( Stars(stars=5, world_size=PIXELS) )


    profile = None
    if args.profiler:
        print "starting profiler"
        import cProfile as profile

        profile = profile.Profile(timeunit=100)
        profile.enable()


    def signal_handler(signal, frame):
        print('\nStopping world run loop\n')
        scene.stop()

    signal.signal(signal.SIGINT, signal_handler)

    scene.run( world_callback )

    if profile:
        import pstats
        profile.disable()

        sortby = 'cumulative'
        ps = pstats.Stats(profile).sort_stats(sortby)

        ps.print_stats(0.25)
        ps.dump_stats("./profile.pf")
