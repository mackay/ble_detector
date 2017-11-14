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

        if self.is_buffer_changed(pixel_buffer):
            self.logger.log(self.log_level, pixels_to_bw(pixel_buffer))


class TextRenderer(Renderer):
    def __init__(self, clear_on_render=False):
        super(TextRenderer, self).__init__()

        self._clear()
        self.clear_on_render = clear_on_render

    def render_buffer(self, pixel_buffer):
        super(TextRenderer, self).render_buffer(pixel_buffer)

        if self.clear_on_render:
            self._clear()

        self._home()

        if self.is_buffer_changed(pixel_buffer):
            self._render_text(pixel_buffer)

    def _clear(self):
        sys.stderr.write("\x1b[2J")

    def _home(self):
        sys.stderr.write("\x1b[H")

    def _render_text(self, pixel_buffer):
        pass


class ConsoleRenderer(TextRenderer):
    def _render_text(self, pixel_buffer):
        print pixels_to_bw(pixel_buffer)


class ConsoleColorRenderer(TextRenderer):

    def _render_text(self, pixel_buffer):
        print pixels_to_ansi_color(pixel_buffer)
