from effects.Effect import Effect


class Turntable(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=50, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        self._iterations = 2
        strip.off()

    def run(self, strip):
        strip.off()
        for i in range(self.pixel_min, self.pixel_max):
            if i % 3 == self._iterations:
                strip.add(position=i, pixel=self.hsv)

        Effect.run(self, strip=strip)

        if self._iterations < 0:
            self._iterations = 2

        return strip
