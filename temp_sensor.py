from math import fmod
from time import sleep, time
import ubinascii
import machine
import dht
import network
import json
from umqtt.simple import MQTTClient

import config

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

sensor  = dht.DHT11(machine.Pin(2))
client = MQTTClient(CLIENT_ID, config.SERVER)

def startup():
    pass

def handle_message(topic, msg):

    print(topic, msg)

    if topic != config.STATE_TOPIC:
        return

next_update = 0
def loop():
    global next_update

    if next_update and next_update < time():
        try:
            sensor.measure()
        except OSError as err:
            print("Cannot read sensor:", err)

        next_update += 30 

        print("%dC %d%%" % (sensor.temperature(), sensor.humidity()))
        client.publish(config.STATE_TOPIC_TEMP, b"%dC" % sensor.temperature())
        client.publish(config.STATE_TOPIC_HUM, b"%d%%" % sensor.humidity())

#    client.check_msg()
#    if not state:
#        return


def setup():
    global next_update

    startup()

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    print("connecting to wifi....")
    while not sta_if.isconnected():
        sleep(1)

    print("Connected with IP", sta_if.ifconfig()[0])

    client.set_callback(handle_message)
    client.connect()
    client.publish(config.DISCOVER_TOPIC_TEMP, 
        json.dumps({
#            "name": config.NAME_TEMP, 
            "state_topic": config.STATE_TOPIC_HUM
        }))
    client.publish(config.DISCOVER_TOPIC_HUM, 
        json.dumps({
#            "name": config.NAME_HUM, 
            "state_topic": config.STATE_TOPIC_TEMP
        }))

    next_update = time()

if __name__ == "__main__":
    setup()
    while True:
        loop()
