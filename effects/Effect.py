class Effect:

    def __init__(self, pixel_max, pixel_min=0, sleep=20, hsv=(0, 0, 0)):
        self.sleep = sleep
        self.hsv = hsv
        self.pixel_max = pixel_max
        self.pixel_min = pixel_min
        self._iterations = 0

    def finished(self):
        return self._iterations < 0

    def run(self, strip):
        self._iterations = self._iterations - 1

    def update(self, sleep=20, hsv=(0, 0, 0)):
        self.hsv = hsv
        self.sleep = sleep