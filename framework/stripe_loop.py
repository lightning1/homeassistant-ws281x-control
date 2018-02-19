import json
from neopixel import *
from hbmqtt.mqtt.constants import QOS_1, QOS_2, QOS_0
from threading import Thread
from systemd import journal
from queue import Empty
from time import sleep
from effects.OneColor import OneColor


# LED strip configuration:
LED_COUNT      = 284     # Number of LED pixels.
#LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


class StripeLoop(Thread):

    def __init__(self, receive_queue, send_queue):
        Thread.__init__(self)
        self._receive_queue = receive_queue
        self._send_queue = send_queue
        journal.send(MESSAGE="LED Thread started")
        self._strip = Adafruit_NeoPixel(LED_COUNT, 10, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        self._strip.begin()
        self._pixels = []
        self._effects = []
        self._last_state = None
        journal.send(MESSAGE="Setting up LED-Thread")

    def run(self):
        while True:
            journal.send(MESSAGE="[begin] Effects active: " + str(len(self._effects)))
            try:
                message = self._receive_queue.get(block=False)
                if message is not None:
                    journal.send(MESSAGE="Process broker message")
                    msg_dict = json.loads(message.decode("utf-8"))

                    # normal one-color operation
                    if self._last_state is not None:
                        last_state = self._last_state
                        journal.send(MESSAGE="Applied last state: " + str(last_state))
                    else:
                        journal.send(MESSAGE="No last state found")
                        last_state = None

                    if 'brightness' not in msg_dict:
                        if last_state is not None and 'brightness' in last_state:
                            msg_dict['brightness'] = int(last_state['brightness'])
                        else:
                            msg_dict['brightness'] = 128
                    else:
                        msg_dict['brightness'] = int(msg_dict['brightness'])

                    if 'color' not in msg_dict:
                        if last_state is not None:
                            msg_dict['color'] = {}
                            msg_dict['color']['r'] = last_state['color']['r']
                            msg_dict['color']['g'] = last_state['color']['g']
                            msg_dict['color']['b'] = last_state['color']['b']
                        else:
                            msg_dict['color'] = {}
                            msg_dict['color']['r'] = 255
                            msg_dict['color']['g'] = 255
                            msg_dict['color']['b'] = 255

                    if 'transition' in msg_dict:
                        transition = int(msg_dict['transition'])
                    else:
                        transition = None

                    if msg_dict['state'] == 'OFF':
                        for effect in self._effects:
                            effect.off(strip=self._strip)
                        for pixel in self._pixels:
                            pixel.set_color(r=0, g=0, b=0, brightness=0)

                        self._effects = []

                    if last_state is None or last_state != msg_dict:
                        self._send_queue.put(json.dumps(msg_dict).encode('UTF-8'))
                        self._last_state = msg_dict

                    if ('effect' not in msg_dict or msg_dict['effect'] == 'none') and msg_dict['state'] != 'OFF':
                        journal.send(MESSAGE="Applying effect None")
                        self._effects.append(OneColor(pixel_min=0,
                                                      pixel_max=self._strip.numPixels(),
                                                      r=msg_dict['color']['r'],
                                                      g=msg_dict['color']['g'],
                                                      b=msg_dict['color']['b'],
                                                      brightness=msg_dict['brightness']))
                    else:
                        journal.send(MESSAGE="[warning] Unknown effect received")

                    journal.send(MESSAGE="[after] Effects active: " + str(len(self._effects)))

            except Empty:
                pass

            waittime = 100
            i = 0
            effect_buffer = self._effects
            for effect in effect_buffer:
                self._pixels = effect.run(self._pixels)
                if effect.sleep < waittime:
                    waittime = effect.sleep
                if effect.finished():
                    self._effects.remove(effect)
                i = i+1

            for pixel in self._pixels:
                pixel.set_pixel(strip=self._strip)

            self._strip.show()

            sleep(waittime / float(1000))
