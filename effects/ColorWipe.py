from effects.Effect import Effect


class ColorWipe(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=20, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        self._iterations = (pixel_max-pixel_min)*2
        strip.off()

    def run(self, strip):
        if self._iterations > (self.pixel_max-self.pixel_min):
            position = (self.pixel_max-self.pixel_min)*2 - self._iterations
            # growing
            new_pixel = self.hsv
            strip.add(position=position, pixel=new_pixel)
        elif self._iterations <= (self.pixel_max-self.pixel_min):
            # shrinking
            strip.remove(self._iterations)
        Effect.run(self, strip=strip)
        if self._iterations < 0:
            self._iterations = (self.pixel_max - self.pixel_min) * 2

        return strip