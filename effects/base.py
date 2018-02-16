import json
from neopixel import *
from hbmqtt.mqtt.constants import QOS_1, QOS_2, QOS_0

def off(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


def brightf(brightness):
    return int(pow(brightness, 2) / float(255))


def tColor(r, g, b, log, factor=255):
    """takes any RGB value and converts it to proper Color. The Factor multiplies with every value"""
    factor = factor / float(255)
    log.info("[tcolor] Before: r=" + str(r) + " g=" + str(g) + " b=" + str(b) + " factor=" + str(factor))
    b = brightf(b * factor)
    r = brightf(r * factor)
    g = brightf(g * factor)
    log.info("[tcolor] After:  r=" + str(r) + " g=" + str(g) + " b=" + str(b) + " factor=" + str(factor))
    return Color(r, b, g)


async def effect(strip, log, message, topic, broker):
    _last_state = None

    log.info("[ws281x] Base effect started")
    _strip = strip
    _log = log

    # parse topic for led number
    command_string = topic.split('/')
    _log.info("[ws281x] Got task: set led-strip to " + str(message))

    if _last_state is not None:
        last_state = _last_state
        _log.info("[ws281x] Applied last state: " + str(last_state))
    else:
        _log.info("[ws281x] No last state found")
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
    color = tColor(r=int(message['color']['r']),
                        g=int(message['color']['g']),
                        b=int(message['color']['b']),
                        factor=float(message['brightness']),
                        log=log)

    if message['state'] == 'OFF':
        off(strip=strip)
    else:
        # if transition is not None:
            # led.transition(transition, color=color, brightness=brightness)
            # msg_dict.pop('transition', None)
        # else:
        for i in range(0, _strip.numPixels()):
            _strip.setPixelColor(i, color)
        _strip.show()

    if last_state is None or last_state != message:
        broker.publish('/woodie/ws281x/get', json.dumps(message).encode('UTF-8'), qos=QOS_0)
        _last_state = message