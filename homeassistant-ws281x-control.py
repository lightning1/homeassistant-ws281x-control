#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from queue import Queue, Empty
from systemd import journal
from framework.stripe_loop import StripeLoop
import os

send_queues = []
receive_queues = []


def on_connect(client, userdata, flags, rc):
    journal.send(MESSAGE="Connected with result code "+str(rc))

    i = 0
    strip = 'STRIP_' + str(i)
    while strip + '_PIN' in os.environ:
        subscription_topic = os.environ['MQTT_BASE_TOPIC'] + str(i) + "/set"
        client.subscribe(subscription_topic)
        journal.send(MESSAGE="Subscribed to " + subscription_topic)

        i = i + 1
        strip = 'STRIP_' + str(i)


def on_message(client, userdata, msg):
    pre_slashes = os.environ['MQTT_BASE_TOPIC'].count('/')

    queue_number = int(msg.topic.split("/")[pre_slashes])

    journal.send(MESSAGE="Processing message to topic " + msg.topic + " with payload " + str(msg.payload)
                         + " in queue " + str(queue_number))

    receive_queues[queue_number].put(item=msg.payload)


if __name__ == '__main__':
    journal.send(MESSAGE="Starting up")

    led_execs = []

    i = 0
    strip_name = 'STRIP_' + str(i)
    while strip_name + '_PIN' in os.environ:
        receive_queues.append(Queue())
        send_queues.append(Queue())
        led_execs.append(StripeLoop(receive_queue=receive_queues[i], send_queue=send_queues[i], strip=i))
        led_execs[i].start()

        i = i + 1
        strip_name = 'STRIP_' + str(i)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(os.environ['MQTT_HOST'], int(os.environ['MQTT_PORT']), 60)

    client.loop_start()
    while True:
        i = 0
        while i < len(send_queues):
            try:
                message = send_queues[i].get(block=False)
                #if 'command_topic' in message:
                #    topic = "/homeassistant/discovery/light/atrium/config"
                #else:
                topic = os.environ['MQTT_BASE_TOPIC'] + str(i) + "/get"
                journal.send(MESSAGE="Publishing to " + topic + ": " + str(message))
                client.publish(topic, message)
            except Empty:
                pass

            i = i + 1
