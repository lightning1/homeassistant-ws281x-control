# homeassistant-ws281x-control
An daemon to connect a raspberry pi with a ws281x LED stripe to HomeAssistant (via MQTT)

## Getting Started
These instructions will guide you through installation progress.

### Prerequisites
* a already installed version of [Home Assistant](https://home-assistant.io/getting-started/)
* an MQTT-Server (e.g. mosquitto)
```
sudo apt-get install mosquitto
```
* the LED-controlling-library [rpi_ws281x](https://github.com/jgarff/rpi_ws281x)
  * don't forget to follow the cascaded readme-instructions in the python directory (to enable execution without adding the path to every execution)
* python3
```
sudo apt-get install git python3 python3-pip
```

### Installing
First of all you need to download these project.
```
cd /usr/local/src
git clone https://github.com/lightning1/homeassistant-ws281x-control
```
you can use the directory you want, but you need to put the right url in the .service file.

Next modify homeassistant-ws281x.service file. The program needs GPIO-access-rights. So create and insert a user or usergroup with rights, or for testing purpose use the User=root. Change the WorkingDirectory= and ExecStart= to your used directory
```
...
User=nobody
Group=nogroup
WorkingDirectory=/usr/local/src/homeassistant-ws281x-control
ExecStart=/usr/local/src/homeassistant-ws281x-control/homeassistant-ws281x-control.py
...
```

In the homeassistant-ws281x-control file, you can define your LED-strip setup.

After that, copy the homeassistant-ws281x.service and the configuration file homeassistant-ws281x-control to their directories.
```
sudo mv homeassistant-ws281x.service /etc/
sudo mv homeassistant-ws281x-control /etc/systemd/system
```

You need to install the following missing python3-dependencies
```
sudo pip3 install systemd paho-mqtt
```

A sample configuration excerpt for the Home Assistend (configuration.yaml) could be:
```
mqtt:
    broker: localhost

light:
  - platform: mqtt_json
    command_topic: "/woodie/ws281x/0/set"
    state_topic: "/woodie/ws281x/0/get"
    rgb: true
    name: atrium
    brightness: true
    effect: true
    effect_list: ['none', 'colorwipe', 'turntable', 'rainbow', 'colorshoot', 'confetti', 'fire', 'sinelon', 'testcolor']
    retain: true    
```

To run the homeassistant-ws281x-control daemon use
```
sudo systemctl start homeassistant-ws281x.service 
```

You can check for errors with
```
sudo systemctl status homeassistant-ws281x.service
```
and
```
journalctl -f -u homeassistant-ws281x.service 
```


### Execution

run the MQTT broker
```
mosquitto -d
```

(restart Home Assistant)
```
sudo systemctl restart home-assistant@homeassistant.service 
```

(restart homeassistant-ws281x daemon)
```
sudo systemctl restart homeassistant-ws281x.service
```
