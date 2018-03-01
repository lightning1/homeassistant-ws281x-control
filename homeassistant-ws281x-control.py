#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from queue import Queue
from systemd import journal
from framework.stripe_loop import StripeLoop


send_queue = Queue()
receive_queue = Queue()


def on_connect(client, userdata, flags, rc):
    journal.send(MESSAGE="Connected with result code "+str(rc))

    client.subscribe("/woodie/ws281x/set")
    journal.send(MESSAGE="Subscribed")


def on_message(client, userdata, msg):
    journal.send(MESSAGE=msg.topic+" "+str(msg.payload))
    receive_queue.put(item=msg.payload)


if __name__ == '__main__':
    journal.send(MESSAGE="Starting up")

    led_exec = StripeLoop(receive_queue=receive_queue, send_queue=send_queue)
    led_exec.start()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("192.168.4.2", 1883, 60)

    client.loop_start()
    while True:
        message = send_queue.get()
        journal.send(MESSAGE="Publishing: " + str(message))
        #if 'command_topic' in message:
        #    topic = "/homeassistant/discovery/light/atrium/config"
        #else:
        topic = "/woodie/ws281x/get"
        client.publish(topic, message)
        journal.send(MESSAGE="Publishing to " + topic + ": " + str(message))
