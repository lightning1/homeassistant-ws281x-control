from effects.Effect import Effect


class OneColor(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=20, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        strip.off()

    def run(self, strip):
        strip.clear()

        for i in range(self.pixel_min, self.pixel_max):
            strip.add(position=i, pixel=self.hsv)
        Effect.run(self, strip=strip)

        return strip