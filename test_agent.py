#!/usr/bin/env python
import argparse
import sys
import signal


from agent.location import LocationAgent
from display import World, Pixel
from display.atmosphere import Ground

import logging
log = logging.getLogger()


if __name__ == "__main__":
    log.setLevel(logging.INFO)
    logging.basicConfig(format="%(thread)d:%(asctime)s:%(levelname)s:%(module)s :: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--map', type=str, default=None,
                        help='color map in the form of location,red,green,blue,location,...')
    parser.add_argument('-s', '--stale', type=str, default=5*5000,
                        help='stale time in ms')
    parser.add_argument('-w', '--world', type=int, default=90,
                        help='size of the world in pixels')

    parser.add_argument('--virtual', action="store_true", dest="virtual", default=False,
                        help='Use pygame display')
    parser.add_argument('--led', action="store_true", dest="led", default=False,
                        help='Use led display')
    parser.add_argument('--text-color', action="store_true", dest="text_color", default=False,
                        help='Use ansi color text display')
    parser.add_argument('--text', action="store_true", dest="text", default=False,
                        help='Use text display')

    parser.add_argument('-r', '--rate', type=int, default=500,
                        help="trigger display rate in ms for each active beacon (affects sprite creation, smaller number = more sprites)")

    parser.add_argument('url', type=str, help="base api url in the form of http[s]://host:port/api")

    arg = parser.parse_args(sys.argv[1:])

    location_color_map = None
    if arg.map:
        location_color_map = { }
        map_tuple = [ ]
        for token in arg.map.split(","):
            map_tuple.append(token)

            if len(map_tuple) == 4:
                location_color_map[map_tuple[0]] = Pixel( int(map_tuple[1]),
                                                          int(map_tuple[2]),
                                                          int(map_tuple[3]) )
                map_tuple = [ ]

    enable_threading = True
    if arg.virtual:
        enable_threading = False

    world = World(arg.world, enable_threading=enable_threading)
    world.add_sprite( Ground(ground_color=Ground.NIGHT_COLOR, brightness_variance=0.0) )

    if arg.virtual:
        from display.renderers.virtual import PyGameRenderer
        world.add_renderer( PyGameRenderer() )
    if arg.led:
        from display.renderers.led import NeoPixelRenderer
        world.add_renderer( NeoPixelRenderer() )
    if arg.text_color:
        from display.renderers.text import ConsoleColorRenderer
        world.add_renderer( ConsoleColorRenderer(clear_on_render=False) )
    if arg.text:
        from display.renderers.text import ConsoleRenderer
        world.add_renderer( ConsoleRenderer(clear_on_render=False) )

    agent = LocationAgent( arg.url,
                           world,
                           location_color_map=location_color_map,
                           stale_time_ms=arg.stale,
                           trigger_time_ms=arg.rate )

    def signal_handler(signal, frame):
        print('\nStopping world run loop\n')
        agent.stop()
        world.stop()

    signal.signal(signal.SIGINT, signal_handler)

    agent.run()
    world.run()

    while world.run_enable and agent.run_enable:
        pass
