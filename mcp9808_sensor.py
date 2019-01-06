from math import fmod
from time import sleep, time
import ubinascii
import machine
import network
import json
from umqtt.simple import MQTTClient
from machine import I2C
import config

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

i2c = I2C(scl=machine.Pin(5), sda=machine.Pin(4))
address = 24
temp_reg = 0x5
client = MQTTClient(CLIENT_ID, config.SERVER)

def startup():
    pass


def handle_message(topic, msg):

    print(topic, msg)

    if topic != config.STATE_TOPIC:
        return


def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp


next_update = 0
def loop():
    global next_update

    if next_update and next_update < time():
        try:
            temp = i2c.readfrom_mem(address, temp_reg, 2)
            client.publish(config.STATE_TOPIC_TEMP, b"%.1fC" % temp_c(temp))
            print(temp_c(temp))
        except OSError as err:
            print("Cannot read sensor:", err)

        next_update += 30 


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
            "state_topic": config.STATE_TOPIC_HUM
        }))

    next_update = time()

if __name__ == "__main__":
    setup()
    while True:
        loop()
