import json
from threading import Thread
from systemd import journal
from queue import Empty
from time import sleep
from effects import *
from effects.Effect import Effect
from framework.strip import Strip
import traceback
import colorsys


def get_discovery():
    msg = {}
    msg['name'] = "Atrium"
    msg['command_topic'] = "/woodie/ws281x/set"
    msg['state_topic'] = "/woodie/ws281x/get"
    msg['rgb'] = True
    msg['brightness'] = True
    msg['effect'] = True
    msg['retain'] = True
    msg['effects'] = get_effect_names()
    return msg


def construct_effect(effect_name, **kwargs):
    journal.send(MESSAGE="Get " + effect_name + " from " + str(get_effect_names()))
    for effect in Effect.__subclasses__():
        if effect.__name__ == effect_name:
            return effect(**kwargs)
    return None


def get_effect_names():
    return [cls.__name__ for cls in Effect.__subclasses__()]


class StripeLoop(Thread):

    def __init__(self, receive_queue, send_queue):
        Thread.__init__(self)
        self._receive_queue = receive_queue
        self._send_queue = send_queue
        journal.send(MESSAGE="LED Thread started")
        self._strip = Strip()
        self._effects = []
        self._last_state = None
        journal.send(MESSAGE="Found Effects: " + str(get_effect_names()))
        #journal.send(MESSAGE="Setting up auto discovery")
        #send_queue.put(get_discovery())
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

                        if self._last_state is not None:
                            last_state = self._last_state
                            journal.send(MESSAGE="Applied last state: " + str(last_state))
                        else:
                            journal.send(MESSAGE="No last state found")
                            last_state = None

                        if 'state' in msg_dict and msg_dict['state'].lower() == 'off':
                            self._effects.clear()
                            self._strip.off()
                            msg_dict['effect'] = 'none'
                        else:
                            # do custom command stuff (if Milight Remote is used)
                            if 'command' in msg_dict:
                                if msg_dict['command'] == 'mode_speed_down' and global_speed < 150:
                                    global_speed = global_speed + 10
                                elif msg_dict['command'] == 'mode_speed_up' and global_speed > 0:
                                    global_speed = global_speed - 10
                                elif msg_dict['command'] == 'white_mode':
                                    msg_dict.pop('hue', True)
                                    msg_dict['color'] = {}
                                    msg_dict['color']['r'] = 255
                                    msg_dict['color']['g'] = 255
                                    msg_dict['color']['b'] = 255
                                restart_effect = True
                            if 'mode' in msg_dict:
                                if 'effect' not in last_state or last_state['effect'].lower() == 'none':
                                    msg_dict['effect'] = 'colorwipe'
                                else:
                                    msg_dict['effect'] = get_effect_names()[
                                        (get_effect_names().index(last_state['effect']) + 1) % len(get_effect_names())]
                            # normal one-color operation

                            if 'brightness' not in msg_dict:
                                if last_state is not None and 'brightness' in last_state:
                                    msg_dict['brightness'] = int(last_state['brightness'])
                                else:
                                    msg_dict['brightness'] = 128
                            else:
                                msg_dict['brightness'] = int(msg_dict['brightness'])

                            if 'color' not in msg_dict and 'hue' not in msg_dict:
                                if last_state is not None and ('color' in last_state or 'hue' in last_state):
                                    if 'color' in last_state:
                                        msg_dict['color'] = {}
                                        msg_dict['color']['r'] = last_state['color']['r']
                                        msg_dict['color']['g'] = last_state['color']['g']
                                        msg_dict['color']['b'] = last_state['color']['b']
                                    elif 'hue' in last_state:
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

                            if 'effect' not in msg_dict:
                                if last_state is not None and 'effect' in last_state:
                                    msg_dict['effect'] = last_state['effect']

                            if ('effect' not in msg_dict or msg_dict['effect'].lower() == 'none')\
                                    and ('state' not in msg_dict or msg_dict['state'].lower() != 'off'):
                                msg_dict['effect'] = 'none'

                            if last_state is not None and 'effect' in last_state and msg_dict['effect'].lower() == last_state['effect'] and effect_class is not 'Onecolor':
                                # update current effect
                                journal.send(MESSAGE="Updating effect " + str(effect_class))
                                for effect in self._effects:
                                    if 'hue' in msg_dict:
                                        hsv = (
                                        int(msg_dict['hue']) / float(360), 1, msg_dict['brightness'] / float(255))
                                    else:
                                        hsv = colorsys.rgb_to_hsv(r=msg_dict['color']['r'] / float(255),
                                                                  g=msg_dict['color']['g'] / float(255),
                                                                  b=msg_dict['color']['b'] / float(255))
                                        hsv = (hsv[0], hsv[1], msg_dict['brightness'] / float(255))
                                    effect.update(sleep=global_speed, hsv=hsv)
                            elif msg_dict['effect'].lower() == 'none' or msg_dict['effect'].capitalize() in get_effect_names():
                                # start new effect
                                self._effects.clear()
                                if msg_dict['effect'].lower() == 'none':
                                    effect_class = 'Onecolor'
                                else:
                                    effect_class = msg_dict['effect'].capitalize()
                                journal.send(MESSAGE="Applying effect " + str(effect_class))
                                if 'hue' in msg_dict:
                                    hsv = (int(msg_dict['hue']) / float(360), 1, msg_dict['brightness'] / float(255))
                                else:
                                    hsv = colorsys.rgb_to_hsv(r=msg_dict['color']['r'] / float(255),
                                                              g=msg_dict['color']['g'] / float(255),
                                                              b=msg_dict['color']['b'] / float(255))
                                    hsv = (hsv[0], hsv[1], msg_dict['brightness'] / float(255))
                                self._effects.append(construct_effect(effect_name=effect_class,
                                                                      pixel_max=self._strip.get_size(),
                                                                      strip=self._strip,
                                                                      hsv=hsv,
                                                                      sleep=global_speed))
                            else:
                                journal.send(MESSAGE="[warning] Unknown effect '" + str(msg_dict['effect']) + "' received")

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
                            journal.send(MESSAGE="Trying to publish state: " + str(send_dict))
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