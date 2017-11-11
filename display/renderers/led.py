from display import Renderer
from neopixel import Adafruit_NeoPixel
import _rpi_ws281x as ws

# LED strip configuration:
# LED_COUNT      = 40      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
# LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0
# LED_STRIP      = ws.SK6812_STRIP_RGBW


class NeoPixelRenderer(Renderer):
    def __init__(self, led_dma=10, led_strip=ws.SK6812W_STRIP):
        super(NeoPixelRenderer, self).__init__()

        self.led_dma = 10
        self.led_strip = led_strip
        self.strip = None

    def setup(self, pixel_count, world):
        super(NeoPixelRenderer, self).setup(pixel_count, world)

        self.strip = Adafruit_NeoPixel( pixel_count,
                                        LED_PIN,
                                        LED_FREQ_HZ,
                                        self.led_dma,
                                        LED_INVERT,
                                        LED_BRIGHTNESS,
                                        LED_CHANNEL,
                                        self.led_strip)

        self.strip.begin()

        for idx, pixel in enumerate(self.pixel_count):
            self.strip.setPixelColorRGB(idx, 0, 0, 0, 0)

        self.strip.show()

    def render_buffer(self, pixel_buffer):
        super(NeoPixelRenderer, self).render_buffer()

        for idx, pixel in enumerate(pixel_buffer):
            self.strip.setPixelColorRGB(idx, int(pixel.r), int(pixel.g), int(pixel.b))  # , int(pixel.w))

        self.strip.show()
