from effects.Effect import Effect
import random
import math


class Sinelon(Effect):

    def __init__(self, pixel_max, strip, pixel_min=0, sleep=5, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        
        self._ledCount = self.pixel_max - self.pixel_min
        self._iterationCount = self._ledCount * 2
        
        self._iterations = 0
        self._original_sleep = sleep
        self.sleep = sleep

    def update(self, sleep=5, hsv=(0, 0, 0)):
        self._currentColor=hsv[0]

        self._original_sleep = sleep
        self.sleep = sleep
        Effect.update(self, sleep, hsv)

    def run(self, strip):

        #dim all pixel
        for i in range(self.pixel_min, self.pixel_max):
            currentPixel = strip.get(i)
            if(currentPixel == None):
                strip.add(position=i, pixel = (0, 0, 0))
            else:
                strip.set(position=i, pixel = (currentPixel[0],currentPixel[1],currentPixel[2]*0.9))

        pos = int(self._ledCount * 0.5 * (1 + math.sin((self._iterations / self._iterationCount - 1) * 2 * math.pi)))
        strip.set(position = pos, pixel = self.hsv)


        Effect.run(self, strip=strip)
        
        if self._iterations < 0:
            self._iterations = self._iterationCount

        return strip
