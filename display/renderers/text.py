from display import Renderer
import logging
import sys

from img2txt.pixel_operations import pixels_to_bw
from img2txt.pixel_operations import pixels_to_ansi_color


class LogRenderer(Renderer):

    def __init__(self, log_level=logging.INFO, do_setup=False):
        super(LogRenderer, self).__init__()
        self.logger = logging.getLogger()
        self.log_level = log_level
        self.do_setup = do_setup

    def setup(self, pixel_count, world):
        super(LogRenderer, self).setup(pixel_count, world)

        if self.do_setup:
            self.logger.setLevel(self.log_level)
            logging.basicConfig(format="%(thread)d:%(asctime)s:%(levelname)s:%(module)s :: %(message)s")

    def render_buffer(self, pixel_buffer):
        super(LogRenderer, self).render_buffer(pixel_buffer)
        self.logger.log(self.log_level, pixels_to_bw(pixel_buffer))


class ConsoleRenderer(Renderer):

    def __init__(self, clear_on_render=False):
        super(ConsoleRenderer, self).__init__()

        self.clear_on_render = clear_on_render

    def setup(self, pixel_count, world):
        super(ConsoleRenderer, self).setup(pixel_count, world)

    def render_buffer(self, pixel_buffer):
        super(ConsoleRenderer, self).render_buffer(pixel_buffer)

        if self.clear_on_render:
            sys.stderr.write("\x1b[2J\x1b[H")

        print pixels_to_bw(pixel_buffer)



class ConsoleColorRenderer(Renderer):

    def __init__(self, clear_on_render=False):
        super(ConsoleColorRenderer, self).__init__()

        self.clear_on_render = clear_on_render

    def setup(self, pixel_count, world):
        super(ConsoleColorRenderer, self).setup(pixel_count, world)

    def render_buffer(self, pixel_buffer):
        super(ConsoleColorRenderer, self).render_buffer(pixel_buffer)

        if self.clear_on_render:
            sys.stderr.write("\x1b[2J\x1b[H")

        print pixels_to_ansi_color(pixel_buffer)
