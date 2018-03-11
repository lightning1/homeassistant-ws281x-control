from effects.Effect import Effect
import random


class Confetti(Effect):

    def __init__(self, pixel_max, strip, pixel_min=0, sleep=10, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        
        self._newColorSpeed = 10
        self._newPositionSpeed = 3

        self._newColorTimer = 0
        self._newPositionTimer = 0
        self._currentColor = 0
        self._iterations = 0
        self._original_sleep = 1
        self.sleep=1

    def update(self, sleep=10, hsv=(0, 0, 0)):
        self._currentColor=hsv[0]

        self._original_sleep=1
        self.sleep=1
        Effect.update(self, 1, hsv)

    def run(self, strip):

        #dim all pixel
        for i in range(self.pixel_min, self.pixel_max):
            currentPixel = strip.get(i)
            if(currentPixel == None):
                strip.add(position=i, pixel = (0, 0, 0))
            else:
                strip.set(position=i, pixel = (currentPixel[0],currentPixel[1],currentPixel[2]*0.98))

        #light up new pixel
        if self._newPositionTimer < 0:
            self._newPositionTimer = self._newPositionSpeed
            newDot = random.randint(0, self.pixel_max - self.pixel_min)
            newColor = self._currentColor + random.uniform(-0.15, 0.15)
            if newColor >= 1:
                newColor -= 1.0
            elif newColor < 0:
                newColor += 1.0
            strip.set(position=newDot, pixel = (newColor, self.hsv[1], self.hsv[2]))
        else:
            self._newPositionTimer -= 1

        #switch to next color
        if self._newColorTimer < 0:
            self._newColorTimer = self._newColorSpeed
            self._currentColor += 0.01
        else:
            self._newColorTimer -= 1

        Effect.run(self, strip=strip)
        
        if self._iterations < 0:
            self._iterations = 2

        return strip
