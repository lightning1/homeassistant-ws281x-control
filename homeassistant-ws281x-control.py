import asyncio
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1, QOS_2
import logging
from neopixel import *
import json
from effects.base import effect


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


log = logging.getLogger('homeassistant_ws281x_control')
log.propagate = False
# log.addHandler(JournalHandler()) not supported in python 3.5
effect_count = 0
_strip = None

C = MQTTClient()


async def mqtt_subscriber(loop, log):
    while True:
        try:
            await C.connect('mqtt://192.168.4.2/')
            await C.subscribe([
                    ('/woodie/ws281x/set', QOS_1),
                 ])
            while True:
                message = await C.deliver_message()
                packet = message.publish_packet
                topic = packet.variable_header.topic_name
                msg = packet.payload.data.decode("utf-8")

                print("t:" + topic + " m:" + msg)

                command_string = topic.split('/')
                msg_dict = json.loads(msg)
                log.info("Received Message: " + str(msg))
                if command_string[3] == 'set':
                    if 'effect' not in msg_dict or msg_dict['effect'] == 'None':
                        loop.create_task(effect(strip=_strip, log=log, topic=topic, message=msg_dict, broker=C))
                    else:
                        log.error("Effect '" + str(msg) + "' is unknown!")

            await C.unsubscribe(['/woodie/ws281x/set'])
            await C.disconnect()
        except ClientException as ce:
            log.error("Client exception: %s" % ce)


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)

    loop = asyncio.get_event_loop()
    log.info("WS281x control application is launching")
    try:
        loop.create_task(mqtt_subscriber(loop=loop, log=log))
        # Initialize LED-Strip
        _strip = Adafruit_NeoPixel(LED_COUNT, 10, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        _strip.begin()

        print('starting event loop')
        loop.run_forever()
    finally:
        log.warning("WS281x control application is terminating")
        loop.close()
