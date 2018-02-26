from effects.Effect import Effect

class Testcolor(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=20, hsv=(0,0,0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        self._iterations = 1
        strip.off()

    def run(self, strip):
        range_max = round((self.pixel_max-self.pixel_min)/float(3))

        for i in range(range_max):
            br = i/range_max*self.hsv[2]
            strip.add(position=i+self.pixel_min, pixel=(0, self.hsv[1], br))
            strip.add(position=i+self.pixel_min+range_max, pixel=(1/float(3), self.hsv[1], br))
            strip.add(position=i+self.pixel_min+2*range_max, pixel=(2/float(3), self.hsv[1], br))

