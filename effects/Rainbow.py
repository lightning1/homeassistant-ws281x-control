from effects.Effect import Effect


class Rainbow(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=50, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        self._iterations = (pixel_max - pixel_min)
        strip.off()
        step = 360 / float(pixel_max - pixel_min)

    def run(self, strip):
        strip.clear()
        for i in range(self.pixel_min, self.pixel_max):
            color = 1 / float(self.pixel_max - self.pixel_min)
            hsv = (color*((i+self._iterations) % (self.pixel_max - self.pixel_min)), 1, self.hsv[2])
            strip.add(position=i, pixel=hsv)

        Effect.run(self, strip=strip)

        if self._iterations < 0:
            self._iterations = self.pixel_max - self.pixel_min

        return strip
