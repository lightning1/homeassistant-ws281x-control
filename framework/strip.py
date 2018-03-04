from systemd import journal
from neopixel import *
import colorsys
import os
import math


# LED strip configuration:
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_CORRECTION = 2    # Some Stripes illuminate on lower RGB values than others.
LED_THRESHOLD = 0.02


class Strip:

    def __init__(self, strip_number):
        # preprocess env data

        # number of LED pixels
        if 'STRIP_' + str(strip_number) + '_LED_COUNT' in os.environ:
            self._real_size = int(os.environ['STRIP_' + str(strip_number) + '_LED_COUNT'])
            self._size = self._real_size
        else:
            self._real_size = 100
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
        # Strip type and colour ordering
        if 'STRIP_' + str(strip_number) + '_TYPE' in os.environ:
            type = os.environ['STRIP_' + str(strip_number) + '_TYPE'].lower()
            if type == "ws2811_strip_grb":
                self._type = ws.WS2811_STRIP_GRB
            elif type == "ws2811_strip_brg":
                self._type = ws.WS2811_STRIP_BRG
            elif type == "ws2811_strip_bgr":
                self._type = ws.WS2811_STRIP_BGR
            else:
                self._type = ws.WS2811_STRIP_RGB
        else:
            self._type = ws.WS2811_STRIP_RGB
        # special limits: ignore pixel at the beginning of the strip
        if 'STRIP_' + str(strip_number) + '_OFFSET_BEGIN' in os.environ:
            self._offset_begin = int(os.environ['STRIP_' + str(strip_number) + '_OFFSET_BEGIN'])
            self._size = self._size - self._offset_begin
        else:
            self._offset_begin = 0
        # special limits: ignore pixel at the end of the strip
        if 'STRIP_' + str(strip_number) + '_OFFSET_END' in os.environ:
            self._offset_end = int(os.environ['STRIP_' + str(strip_number) + '_OFFSET_END'])
            self._size = self._size - self._offset_end
        else:
            self._offset_end = 0
        # special limits: set group size (number of pixels accessed as one)
        if 'STRIP_' + str(strip_number) + '_GROUP_SIZE' in os.environ:
            self._group_size = int(os.environ['STRIP_' + str(strip_number) + '_GROUP_SIZE'])
            self._size = math.floor(self._size / self._group_size)
        else:
            self._group_size = 1
        # special limits: set dark/empty pixels of groups
        if 'STRIP_' + str(strip_number) + '_GROUP_EMPTY' in os.environ:
            self._group_empty = int(os.environ['STRIP_' + str(strip_number) + '_GROUP_EMPTY'])
        else:
            self._group_empty = 0
        self._strip = Adafruit_NeoPixel(self._real_size,
                                        self._pin,
                                        LED_FREQ_HZ,
                                        self._dma,
                                        LED_INVERT,
                                        LED_BRIGHTNESS,
                                        LED_CHANNEL,
                                        self._type)
        self._strip.begin()
        self._pixels = {}
        self._strip_number = strip_number
        self.off()

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
        for position in range(0, self._real_size):
            self._strip.setPixelColor(position, Color(0, 0, 0))
        self.clear()

    def loop(self):
        #journal.send(MESSAGE="[debug] BeginOffset: " + str(self._offset_begin) + " GroupSize: " + str(self._group_size)
        #                     + " GroupEmpty: " + str(self._group_empty) + " Size: " + str(self._size))

        for position, pixel in self._pixels.items():
            # add empty start pixels
            real_position = position * self._group_size + self._offset_begin

            rgb = colorsys.hsv_to_rgb(h=pixel[0], s=pixel[1], v=pixel[2])

            if real_position > self._real_size:
                journal.send(MESSAGE="[ERROR] real_position: " + str(real_position) + " size: " + str(self._real_size))

            for i in range(0, (self._group_size - self._group_empty)):
                self._strip.setPixelColor(real_position + i, Color(int(rgb[0] * 255), int(rgb[2] * 255), int(rgb[1] * 255)))
            #if any([position < 100,  position > 183]) and pixel[2] < LED_THRESHOLD:
            #    rgb = colorsys.hsv_to_rgb(h=pixel[0], s=pixel[1], v=pixel[2]*LED_CORRECTION)
            #    self._strip.setPixelColor(position, Color(int(rgb[0] * 255 + 1), int(rgb[2] * 255 + 1), int(rgb[1] * 255 + 1)))
            #else:
            #    rgb = colorsys.hsv_to_rgb(h=pixel[0], s=pixel[1], v=pixel[2])
            #    self._strip.setPixelColor(position, Color(int(rgb[0] * 255), int(rgb[2] * 255), int(rgb[1] * 255)))

        self._strip.show()
        #journal.send(MESSAGE="[loop] Got " + str(len(self._pixels)) + " pixels configured")

    def get_size(self):
        journal.send(MESSAGE="SIZE OF " + str(self._size) + " REAL: " + str(self._real_size))
        return self._size
