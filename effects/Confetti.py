from effects.Effect import Effect
import random


class Confetti(Effect):

    def __init__(self, pixel_max, strip, pixel_min=0, sleep=10, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)
        
        self._newColorSpeed = 5
        self._newPositionSpeed = 2

        self._newColorTimer = 0
        self._newPositionTimer = 0
        self._currentColor = 0
        self._iterations = 0
        self._original_sleep = 1
        self.sleep=1

        # pixel dict
        #self._pixels = []
        # time for a single fading step
        #self._fading_time = 10
        # currently fading pixel
        #self._current_pixel = None
        # possible states:
        #   growing: starting to light up things
        #self._state = 'begin'
        #self.sleep = self._fading_time


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
            newColor = self._currentColor + random.uniform(0.0, 0.2)
            if newColor >= 1:
                newColor -= 1.0
            strip.set(position=newDot, pixel = (newColor, 0.78, self.hsv[2]))
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

#        if self._state == 'begin':
#            # growing is starting
#            strip.off()
#            self._pixels = list(range(self.pixel_min, self.pixel_max))
#            random.shuffle(self._pixels)
#            self._state = 'growing'
#        elif self._state == 'growing' and len(self._pixels) == 0:
#            # growing is finished
#            self._state = 'shrinking'
#            self._pixels = list(range(self.pixel_min, self.pixel_max))
#            random.shuffle(self._pixels)
#        elif self._state == 'growing':
#            # grow a pixel
#            # is there already a pixel growing?
#            if self._current_pixel is None:
#                # no pixel growing
#                self._current_pixel = self._pixels.pop()
#                strip.add(position=self._current_pixel, pixel=(self.hsv[0], self.hsv[1], 0.001))
#            else:
#                now = strip.get(self._current_pixel)
#                if now[2] > self.hsv[2]:
#                    # pixel is finished
#                    strip.set(position=self._current_pixel, pixel=self.hsv)
#                    self._current_pixel = None
#                else:
#                    # pixel is still growing
#                    # calculate step size
#                    adding = self.hsv[2] / (self._original_sleep / float(self._fading_time))
#                    strip.set(position=self._current_pixel, pixel=(self.hsv[0], self.hsv[1], now[2] + adding))
#        elif self._state == 'shrinking':
#            # shrink a pixel
#            # is there already a pixel in move?
#            if self._current_pixel is None:
#                # no pixel growing
#                self._current_pixel = self._pixels.pop()
#                strip.add(position=self._current_pixel, pixel=(self.hsv[0], self.hsv[1], self.hsv[2]))
#            else:
#                now = strip.get(self._current_pixel)
#                if now[2] <= 0:
#                    # pixel is finished
#                    strip.remove(position=self._current_pixel)
#                    self._current_pixel = None
#                else:
#                    # pixel is still shrinking
#                    # calculate step size
#                    adding = self.hsv[2] / (self._original_sleep / float(self._fading_time))
#                    strip.set(position=self._current_pixel, pixel=(self.hsv[0], self.hsv[1], now[2] - adding))
