from effects.Effect import Effect
from framework.pixel import Pixel


class ColorWipe(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=20, r=0, g=0, b=0, brightness=255):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, r=r, g=g, b=b, brightness=brightness)
        self._iterations = (pixel_max-pixel_min)*2
        strip.off()

    def run(self, strip):
        if self._iterations > (self.pixel_max-self.pixel_min):
            position = (self.pixel_max-self.pixel_min)*2 - self._iterations
            # growing
            new_pixel = Pixel(r=self.r, g=self.g, b=self.b, brightness=self.brightness)
            strip.add(position=position, pixel=new_pixel)
        elif self._iterations <= (self.pixel_max-self.pixel_min):
            # shrinking
            strip.remove(self._iterations)
        Effect.run(self, strip=strip)
        if self._iterations < 0:
            self._iterations = (self.pixel_max - self.pixel_min) * 2

        return strip