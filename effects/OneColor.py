from effects.Effect import Effect
from framework.pixel import Pixel


class OneColor(Effect):
    def __init__(self, pixel_max, pixel_min=0, sleep=20, r=0, g=0, b=0, brightness=255):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, r=r, g=g, b=b, brightness=brightness)

    def run(self, pixels):
        pixels = []
        for i in range(self.pixel_min, self.pixel_max):
            pixels.append(Pixel(pos=i, r=self.r, g=self.g, b=self.b, brightness=self.brightness))
        Effect.run(self, pixels=pixels)

        return pixels