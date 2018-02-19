from systemd import journal
from neopixel import *


# LED strip configuration:
LED_COUNT      = 284     # Number of LED pixels.
#LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


class Strip:

    def __init__(self):
        self._size = LED_COUNT
        self._strip = Adafruit_NeoPixel(LED_COUNT, 10, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        self._strip.begin()
        self._pixels = {}

    def clear(self):
        self._pixels.clear()

    def get(self, position):
        if position in self._pixels.keys():
            return self._pixels[position]
        else:
            return None

    def get_all(self):
        return list(self._pixels.values())

    def remove(self, position):
        if position in self._pixels.keys():
            self._pixels.pop(position)
            self._strip.setPixelColor(position, Color(0, 0, 0))

    def add(self, pixel, position):
        if position in self._pixels.keys():
            journal.send(MESSAGE="[warning] Trying to add pixel on position " + str(position)
                                 + ", but there's already one!")
        elif position > self._size:
            journal.send(MESSAGE="[warning] Trying to add pixel on position " + str(position)
                                 + ", but the stripe only has " + str(self._size) + " pixels!")
        else:
            self._pixels[position] = pixel

    def off(self):
        for position in self._pixels.keys():
            self._strip.setPixelColor(position, Color(0, 0, 0))
        self.clear()

    def loop(self):
        for position, pixel in self._pixels.items():
            self._strip.setPixelColor(position, Color(pixel._r, pixel._b, pixel._g))
        self._strip.show()
        #journal.send(MESSAGE="[loop] Got " + str(len(self._pixels)) + " pixels configured")

    def get_size(self):
        return self._size