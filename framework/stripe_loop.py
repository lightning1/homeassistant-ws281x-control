import json
from hbmqtt.mqtt.constants import QOS_1, QOS_2, QOS_0
from threading import Thread
from systemd import journal
from queue import Empty
from time import sleep
from effects.ColorWipe import ColorWipe
from effects.OneColor import OneColor
from effects.Turntable import Turntable
from framework.strip import Strip
import traceback


class StripeLoop(Thread):

    def __init__(self, receive_queue, send_queue):
        Thread.__init__(self)
        self._receive_queue = receive_queue
        self._send_queue = send_queue
        journal.send(MESSAGE="LED Thread started")
        self._strip = Strip()
        self._effects = []
        self._last_state = None
        journal.send(MESSAGE="Setting up LED-Thread")

    def run(self):
        while True:
            try:
                try:
                    message = self._receive_queue.get(block=False)
                    if message is not None:
                        journal.send(MESSAGE="[begin] Effects active: " + str(len(self._effects)))
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
                            self._effects.clear()
                            self._strip.off()

                        if ('effect' not in msg_dict or msg_dict['effect'] == 'none') and msg_dict['state'] != 'OFF':
                            self._effects.clear()
                            journal.send(MESSAGE="Applying effect OneColor")
                            self._effects.append(OneColor(pixel_max=self._strip.get_size(),
                                                          strip=self._strip,
                                                          r=msg_dict['color']['r'],
                                                          g=msg_dict['color']['g'],
                                                          b=msg_dict['color']['b'],
                                                          brightness=msg_dict['brightness']))
                            msg_dict['effect'] = 'none'
                        elif 'effect' in msg_dict:
                            if msg_dict['effect'] == 'colorwipe':
                                self._effects.clear()
                                journal.send(MESSAGE="Applying effect ColorWipe")
                                self._effects.append(ColorWipe(pixel_max=self._strip.get_size(),
                                                               strip=self._strip,
                                                               r=msg_dict['color']['r'],
                                                               g=msg_dict['color']['g'],
                                                               b=msg_dict['color']['b'],
                                                               brightness=msg_dict['brightness']))
                            elif msg_dict['effect'] == 'turntable':
                                self._effects.clear()
                                journal.send(MESSAGE="Applying effect Turntable")
                                self._effects.append(Turntable(pixel_max=self._strip.get_size(),
                                                               strip=self._strip,
                                                               r=msg_dict['color']['r'],
                                                               g=msg_dict['color']['g'],
                                                               b=msg_dict['color']['b'],
                                                               brightness=msg_dict['brightness']))
                            else:
                                journal.send(MESSAGE="[warning] Unknown effect received")

                        if last_state is None or last_state != msg_dict:
                            self._send_queue.put(json.dumps(msg_dict).encode('UTF-8'))
                            self._last_state = msg_dict

                        journal.send(MESSAGE="[after] Effects active: " + str(len(self._effects)))

                except Empty:
                    pass

                waittime = 100
                i = 0
                effect_buffer = self._effects
                for effect in effect_buffer:
                    effect.run(self._strip)
                    if effect.sleep < waittime:
                        waittime = effect.sleep
                    if effect.finished():
                        self._effects.remove(effect)
                    i = i+1

                self._strip.loop()

                sleep(waittime / float(1000))
            except:
                journal.send(MESSAGE=traceback.format_exc())