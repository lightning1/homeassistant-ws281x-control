class Effect:

    def __init__(self, pixel_max, pixel_min=0, sleep=20, r=0, g=0, b=0, brightness=255):
        self.sleep = sleep
        self.r = r
        self.g = g
        self.b = b
        self.brightness = brightness
        self.pixel_max = pixel_max
        self.pixel_min = pixel_min
        self._iterations = 0

    def finished(self):
        return self._iterations <= 0

    def run(self, pixels):
        self._iterations = self._iterations - 1