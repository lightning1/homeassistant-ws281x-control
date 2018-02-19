from effects.Effect import Effect
from framework.pixel import Pixel


class Turntable(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=50, r=0, g=0, b=0, brightness=255):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, r=r, g=g, b=b, brightness=brightness)
        self._iterations = 2
        strip.off()

    def run(self, strip):
        strip.off()
        for i in range(self.pixel_min, self.pixel_max):
            if i % 3 == self._iterations:
                strip.add(position=i, pixel=Pixel(r=self.r, g=self.g, b=self.b, brightness=self.brightness))

        Effect.run(self, strip=strip)

        if self._iterations < 0:
            self._iterations = 2

        return strip
