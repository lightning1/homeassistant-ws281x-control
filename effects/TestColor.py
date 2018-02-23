from effects.Effect import Effect
from framework.pixel import Pixel

class TestColor(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=20, r=0, g=0, b=0, brightness=255):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, r=r, g=g, b=b, brightness=brightness)
        self._iterations = 1
        strip.off()

    def run(self, strip):
        range_max = round((self.pixel_max-self.pixel_min)/float(3))

        for i in range(range_max):
            br = i/range_max
            red_pixel = Pixel(r=self.r, brightness=br)
            green_pixel = Pixel(g=self.g, brightness=br)
            blue_pixel = Pixel(b=self.b, brightness=br)
            strip.add(position=i+self.pixel_min, red_pixel)
            strip.add(position=i+self.pixel_min+range_max, green_pixel)
            strip.add(position=i+self.pixel_min+2*range_max, blue_pixel)

