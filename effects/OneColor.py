from effects.Effect import Effect
from framework.pixel import Pixel


class OneColor(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=20, r=0, g=0, b=0, brightness=255):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, r=r, g=g, b=b, brightness=brightness)
        strip.off()

    def run(self, strip):
        strip.clear()

        for i in range(self.pixel_min, self.pixel_max):
            strip.add(position=i, pixel=Pixel(r=self.r, g=self.g, b=self.b, brightness=self.brightness))
        Effect.run(self, strip=strip)

        return strip