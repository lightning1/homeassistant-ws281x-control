class Pixel:
    @staticmethod
    def _dimmer(i, brightness=255):
        factor = brightness / float(255)
        return int(int(pow(i * factor, 2)) / float(255))

    def __init__(self, r=0, g=0, b=0, brightness=255):
        self.r = r
        self.g = g
        self.b = b
        self.brightness = brightness
        self._r = self._dimmer(i=r, brightness=brightness)
        self._g = self._dimmer(i=g, brightness=brightness)
        self._b = self._dimmer(i=b, brightness=brightness)

    def get_brightness(self):
        return self.brightness

    def get_r(self):
        return self.r

    def get_calculated_r(self):
        return self._r

    def get_g(self):
        return self.g

    def get_calculated_g(self):
        return self._g

    def get_b(self):
        return self.b

    def get_calculated_b(self):
        return self._b

    def set_color(self, r=0, g=0, b=0, brightness=255):
        self.__init__(pos=self._pos, r=r, g=g, b=b, brightness=brightness)