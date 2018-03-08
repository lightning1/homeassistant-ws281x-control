from effects.Effect import Effect
import random


class Fire(Effect):

    def __init__(self, pixel_max, strip, pixel_min=0, sleep=50, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
       
        self._heatsteps = self.pixel_max - self.pixel_min
        self._heat = [0] * self._heatsteps
        self._cooling = 0.8 
        self._sparking = 100
        
#        self._newColorSpeed = 5
#        self._newPositionSpeed = 2
#
#        self._newColorTimer = 0
#        self._newPositionTimer = 0
#        self._currentColor = 0
        self._iterations = 0
        self._original_sleep = sleep
        self.sleep = sleep

    def update(self, sleep=50, hsv=(0, 0, 0)):
#        self._currentColor=hsv[0]

        self._original_sleep=sleep
        self.sleep=sleep
        Effect.update(self, sleep, hsv)

    def run(self, strip):

        strip.off()
        for i in range(0, self._heatsteps-1):
            self._heat[i] = self._heat[i] * random.uniform(self._cooling, 1.0)
        for k in range(self._heatsteps-2,3,-1):
            self._heat[k] = (self._heat[k-1] + self._heat[k-2] + self._heat[k-2]) / 3
        if random.randint(0, self._heatsteps) < self._sparking:
            y = random.randint(0,7)
            self._heat[y] += random.uniform(0.63, 1.0)
        for j in range(0, self._heatsteps-1):
            if self._heat[j] < 0:
                self._heat[j] = 0
            elif self._heat[j] > 1:
                self._heat[j] = 1

            if self._heat[j] < 0.33:
                strip.add(position=j, pixel = (self.hsv[0], 1.0, self._heat[j] * 3 * self.hsv[2]))
            elif self._heat[j] < 0.66:
                strip.add(position=j, pixel = (self.hsv[0] + (self._heat[j] - 0.33) * 0.5, 1.0, 1.0 * self.hsv[2]))
            else:
                strip.add(position=j, pixel = (self.hsv[0] + 0.17, 1.0 - (self._heat[j] - 0.66) * 3, 1.0 * self.hsv[2]))

        Effect.run(self, strip=strip)
        
        if self._iterations < 0:
            self._iterations = 2

        return strip
