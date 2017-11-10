from display.scene import Scene
from neopixel import Adafruit_NeoPixel, ws

# LED strip configuration:
# LED_COUNT      = 40      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
# LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0
# LED_STRIP      = ws.SK6812_STRIP_RGBW


class NeoPixelScene(Scene):
    def __init__(self, pixel_count, led_dma=10, led_strip=ws.SK6812_STRIP_RGBW):
        super(NeoPixelScene, self).__init__(pixel_count)

        self.led_dma = 10
        self.led_strip = led_strip
        self.strip = None

    def __init_pixels(self):
        self.strip = Adafruit_NeoPixel( len(self.pixels),
                                        LED_PIN,
                                        LED_FREQ_HZ,
                                        self.led_dma,
                                        LED_INVERT,
                                        LED_BRIGHTNESS,
                                        LED_CHANNEL,
                                        self.led_strip)

        self.strip.begin()

    def render(self):
        super(NeoPixelScene, self).render()

        for idx, pixel in enumerate(self.pixels):
            self.strip.setPixelColorRGB(idx, pixel.r, pixel.g, pixel.b, pixel.w)

        self.strip.show()
