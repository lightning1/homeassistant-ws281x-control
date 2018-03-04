from systemd import journal
from neopixel import *
import colorsys
import os


# LED strip configuration:
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
LED_CORRECTION = 2    # Some Stripes illuminate on lower RGB values than others.
LED_THRESHOLD = 0.02


class Strip:

    def __init__(self, strip_number):
        # preprocess env data

        # number of LED pixels
        if 'STRIP_' + str(strip_number) + '_LED_COUNT' in os.environ:
            self._size = int(os.environ['STRIP_' + str(strip_number) + '_LED_COUNT'])
        else:
            self._size = 100
            journal.send(MESSAGE="[warning] No size (led count) for strip " + str(strip_number)
                                 + " was configured! Fallback to default (100).")
        # GPIO pin connected to the pixels (18 uses PWM, 10 uses SPI /dev/spidev0.0)
        if 'STRIP_' + str(strip_number) + '_PIN' in os.environ:
            self._pin = int(os.environ['STRIP_' + str(strip_number) + '_PIN'])
        else:
            journal.send(MESSAGE="[error] No control pin for strip " + str(strip_number)
                                 + " was configured! Strip is not operational.")
        # DMA channel to use for generating signal (try 10)
        if 'STRIP_' + str(strip_number) + '_DMA' in os.environ:
            self._dma = int(os.environ['STRIP_' + str(strip_number) + '_DMA'])
        else:
            self._dma = 10
            journal.send(MESSAGE="[warning] No DMA channel for strip " + str(strip_number)
                                 + " was configured! Fallback to default (10).")
        self._strip = Adafruit_NeoPixel(self._size,
                                        self._pin,
                                        LED_FREQ_HZ,
                                        self._dma,
                                        LED_INVERT,
                                        LED_BRIGHTNESS,
                                        LED_CHANNEL,
                                        LED_STRIP)
        self._strip.begin()
        self._pixels = {}
        self._strip_number = strip_number

    def clear(self):
        self._pixels.clear()

    def get(self, position):
        if position in self._pixels.keys():
            return self._pixels[position]
        else:
            return None

    def set(self, position, pixel):
        self._pixels[position] = pixel

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
            if any([position < 100,  position > 183]) and pixel[2] < LED_THRESHOLD:
                rgb = colorsys.hsv_to_rgb(h=pixel[0], s=pixel[1], v=pixel[2]*LED_CORRECTION)
                self._strip.setPixelColor(position, Color(int(rgb[0] * 255 + 1), int(rgb[2] * 255 + 1), int(rgb[1] * 255 + 1)))
            else:
                rgb = colorsys.hsv_to_rgb(h=pixel[0], s=pixel[1], v=pixel[2])
                self._strip.setPixelColor(position, Color(int(rgb[0] * 255), int(rgb[2] * 255), int(rgb[1] * 255)))

        self._strip.show()
        #journal.send(MESSAGE="[loop] Got " + str(len(self._pixels)) + " pixels configured")

    def get_size(self):
        return self._size