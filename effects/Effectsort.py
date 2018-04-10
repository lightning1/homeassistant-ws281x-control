from effects.Effect import Effect
import random


class Effectsort(Effect):
    def __init__(self, pixel_max, strip, pixel_min=0, sleep=50, hsv=(0, 0, 0)):
        Effect.__init__(self, pixel_max=pixel_max, pixel_min=pixel_min, sleep=sleep, hsv=hsv)

        self.shuffled_list = []
        k = 0
        for i in range(0,1,float(1)/(self.pixel_max-self.pixel_min)):
            self.shuffled_list[k] = i
            k += 1
        random.shuffle(self.shuffled_list)

        self.sort_speed = 3
        self.sort_timer = 0

        self.bubble_max = len(self.shuffled_list)
        self.bubble_step = 0

        self._iterations = len(self.shuffled_list) - 1

    def run(self, strip):

        # Set all pixels to current color
        k = 0
        for i in range(self.pixel_min, self.pixel_max):
            currentPixel = strip.get(i)
            if(currentPixel == None):
                strip.add(position=i, pixel = (0, 0, 0))
            else:
                strip.set(position=i, pixel = (self.hsv[0],self.hsv[1],self.shuffled_list[k]))
            k += 1

        # Check for speed
        if self.sort_timer > 0:
            self.sort_timer -= 1
        else:
            self.sort_timer = self.sort_speed
            # One step bubblesort
            if self.bubble_step + 1 < self.bubble_max: # Still within current iteration?
                if self.shuffled_list[self.bubble_step] > self.shuffled_list[self.bubble_step+1]: # Compare current and next element
                    temp = self.shuffled_list[self.bubble_step]
                    self.shuffled_list[self.bubble_step] = self.shuffled_list[self.bubble_step+1]
                    self.shuffled_list[self.bubble_step+1] = temp
                self.bubble_step += 1
            else: # One Iteration done
                self.bubble_max -= 1
                self.bubble_step = 0
                self._iterations -= 1
            if self.bubble_max <= 1: # Shuffle List again when finished
                random.shuffle(self.shuffled_list)
                self.bubble_max = len(self.shuffled_list)
                self.bubble_step = 0
                self._iterations = len(self.shuffled_list) - 1

        return strip
