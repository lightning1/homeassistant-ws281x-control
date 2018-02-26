import json
from hbmqtt.mqtt.constants import QOS_1, QOS_2, QOS_0
from threading import Thread
from systemd import journal
from queue import Empty
from time import sleep
from effects.ColorWipe import ColorWipe
from effects.OneColor import OneColor
from effects.Turntable import Turntable
from effects.Rainbow import Rainbow
from framework.strip import Strip
import traceback
import colorsys


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
        global_speed = 50
        while True:
            try:
                try:
                    restart_effect = False
                    message = self._receive_queue.get(block=False)
                    if message is not None:
                        journal.send(MESSAGE="[begin] Effects active: " + str(len(self._effects)))
                        journal.send(MESSAGE="Process broker message")
                        msg_dict = json.loads(message.decode("utf-8"))

                        # do custom command stuff (if Milight Remote is used)
                        if 'command' in msg_dict:
                            if msg_dict['command'] == 'mode_speed_down' and global_speed < 150:
                                global_speed = global_speed + 10
                            elif msg_dict['command'] == 'mode_speed_up' and global_speed > 0:
                                global_speed = global_speed - 10
                            restart_effect = True

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

                        if 'color' not in msg_dict and 'hue' not in msg_dict:
                            if last_state is not None:
                                if 'color' in last_state:
                                    msg_dict['color'] = {}
                                    msg_dict['color']['r'] = last_state['color']['r']
                                    msg_dict['color']['g'] = last_state['color']['g']
                                    msg_dict['color']['b'] = last_state['color']['b']
                                else:
                                    msg_dict['hue'] = last_state['hue']
                            else:
                                msg_dict['color'] = {}
                                msg_dict['color']['r'] = 255
                                msg_dict['color']['g'] = 255
                                msg_dict['color']['b'] = 255

                        if 'transition' in msg_dict:
                            transition = int(msg_dict['transition'])
                        else:
                            transition = None

                        if 'state' in msg_dict and msg_dict['state'].lower() == 'off':
                            self._effects.clear()
                            self._strip.off()
                            msg_dict['effect'] = 'none'

                        if 'effect' not in msg_dict:
                            if last_state is not None and 'effect' in last_state:
                                msg_dict['effect'] = last_state['effect']

                        if ('effect' not in msg_dict or msg_dict['effect'].lower() == 'none')\
                                and ('state' not in msg_dict or msg_dict['state'].lower() != 'off'):
                            self._effects.clear()
                            journal.send(MESSAGE="Applying effect OneColor")
                            if 'hue' in msg_dict:
                                hsv = (int(msg_dict['hue']) / float(360), 1, msg_dict['brightness'] / float(255))
                            else:
                                hsv = colorsys.rgb_to_hsv(r=msg_dict['color']['r'] / float(255),
                                                          g=msg_dict['color']['g'] / float(255),
                                                          b=msg_dict['color']['b'] / float(255))
                                hsv = (hsv[0], hsv[1], msg_dict['brightness'] / float(255))
                            self._effects.append(OneColor(pixel_max=self._strip.get_size(),
                                                          strip=self._strip,
                                                          hsv=hsv))
                            msg_dict['effect'] = 'none'
                        elif 'effect' in msg_dict:
                            if msg_dict['effect'].lower() == 'colorwipe':
                                self._effects.clear()
                                journal.send(MESSAGE="Applying effect ColorWipe")
                                if 'hue' in msg_dict:
                                    hsv = (int(msg_dict['hue']) / float(360), 1, msg_dict['brightness'] / float(255))
                                else:
                                    hsv = colorsys.rgb_to_hsv(r=msg_dict['color']['r'] / float(255),
                                                              g=msg_dict['color']['g'] / float(255),
                                                              b=msg_dict['color']['b'] / float(255))
                                hsv = (hsv[0], hsv[1], msg_dict['brightness'] / float(255))
                                self._effects.append(ColorWipe(pixel_max=self._strip.get_size(),
                                                               strip=self._strip,
                                                               hsv=hsv,
                                                               sleep=global_speed))
                            elif msg_dict['effect'].lower() == 'turntable':
                                self._effects.clear()
                                journal.send(MESSAGE="Applying effect Turntable")
                                if 'hue' in msg_dict:
                                    hsv = (int(msg_dict['hue']) / float(360), 1, msg_dict['brightness'] / float(255))
                                else:
                                    hsv = colorsys.rgb_to_hsv(r=msg_dict['color']['r'] / float(255),
                                                              g=msg_dict['color']['g'] / float(255),
                                                              b=msg_dict['color']['b'] / float(255))
                                hsv = (hsv[0], hsv[1], msg_dict['brightness'] / float(255))
                                self._effects.append(Turntable(pixel_max=self._strip.get_size(),
                                                               strip=self._strip,
                                                               hsv=hsv,
                                                               sleep=global_speed))
                            elif msg_dict['effect'].lower() == 'rainbow':
                                self._effects.clear()
                                journal.send(MESSAGE="Applying effect Rainbow")
                                if 'hue' in msg_dict:
                                    hsv = (int(msg_dict['hue']) / float(360), 1, msg_dict['brightness'] / float(255))
                                else:
                                    hsv = colorsys.rgb_to_hsv(r=msg_dict['color']['r'] / float(255),
                                                              g=msg_dict['color']['g'] / float(255),
                                                              b=msg_dict['color']['b'] / float(255))
                                hsv = (hsv[0], hsv[1], msg_dict['brightness'] / float(255))
                                self._effects.append(Rainbow(pixel_max=self._strip.get_size(),
                                                             strip=self._strip,
                                                             hsv=hsv,
                                                             speed=global_speed))
                            else:
                                journal.send(MESSAGE="[warning] Unknown effect received")

                        if last_state is None or last_state != msg_dict:
                            send_dict = msg_dict
                            if 'hue' in msg_dict:
                                # homeassistant can not display hue value, so converting it to rgb
                                rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
                                send_dict['color'] = {}
                                send_dict['color']['r'] = int(rgb[0]*255)
                                send_dict['color']['g'] = int(rgb[1]*255)
                                send_dict['color']['b'] = int(rgb[2]*255)
                                send_dict.pop('hue')
                            if 'state' not in send_dict:
                                send_dict['state'] = 'ON'
                            self._send_queue.put(json.dumps(send_dict).encode('UTF-8'))
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