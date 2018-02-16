import json
from neopixel import *


class Effect:
    _mqtt = None
    _pin = None
    _last_state = None
    _strip = None
    _log = None

    def off(self):
        for i in range(self._strip.numPixels()):
            self._strip.setPixelColor(i, Color(0, 0, 0))
        self._strip.show()

    def brightf(self, brightness):
        return int(pow(brightness, 2) / float(255))

    def tColor(self, r, g, b, factor=255):
        """takes any RGB value and converts it to proper Color. The Factor multiplies with every value"""
        factor = factor / float(255)
        self._log.info("[tcolor] Before: r=" + str(r) + " g=" + str(g) + " b=" + str(b) + " factor=" + str(factor))
        b = self.brightf(b * factor)
        r = self.brightf(r * factor)
        g = self.brightf(g * factor)
        self._log.info("[tcolor] After:  r=" + str(r) + " g=" + str(g) + " b=" + str(b) + " factor=" + str(factor))
        return Color(r, b, g)

    def __init__(self, strip, log, message, topic, broker):
        log.info(MESSAGE="[ws281x] Base effect started")
        self._strip = strip
        self._log = log

        # parse topic for led number
        command_string = topic.split('/')
        self._log.info("[ws281x] Got task: set led-strip to " + str(message))

        if self._last_state is not None:
            last_state = self._last_state
            self._log.info("[ws281x] Applied last state: " + str(last_state))
        else:
            self._log.info("[ws281x] No last state found")
            last_state = None

        if 'brightness' not in message:
            if last_state is not None and 'brightness' in last_state:
                message['brightness'] = int(last_state['brightness'])
            else:
                message['brightness'] = 128
        else:
            message['brightness'] = int(message['brightness'])

        if 'color' not in message:
            if last_state is not None:
                message['color'] = {}
                message['color']['r'] = last_state['color']['r']
                message['color']['g'] = last_state['color']['g']
                message['color']['b'] = last_state['color']['b']
            else:
                message['color'] = {}
                message['color']['r'] = 255
                message['color']['g'] = 255
                message['color']['b'] = 255

        if 'transition' in message:
            transition = int(message['transition'])
        else:
            transition = None

        # preprocess dict values
        color = self.tColor(r=int(message['color']['r']),
                            g=int(message['color']['g']),
                            b=int(message['color']['b']),
                            factor=float(message['brightness']))

        if message['state'] == 'OFF':
            self.off()
        else:
            # if transition is not None:
                # led.transition(transition, color=color, brightness=brightness)
                # msg_dict.pop('transition', None)
            # else:
            for i in range(0, self._strip.numPixels()):
                self._strip.setPixelColor(i, color)
            self._strip.show()

        if last_state is None or last_state != message:
            broker.publish('/woodie/ws281x/get', json.dumps(message).encode('UTF-8'), qos=QOS_0)
            self._last_state = message