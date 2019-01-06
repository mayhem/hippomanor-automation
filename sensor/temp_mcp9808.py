from math import fmod
from time import sleep, time
import ubinascii
import machine
import network
import json
from umqtt.simple import MQTTClient
from machine import I2C
import net_config
import _config as config
from influx import post_points

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
STATE_TOPIC = b"home/%s/state" % config.NODE_ID
DISCOVER_TOPIC = b"homeassistant/sensor/%s/config" % config.NODE_ID

i2c = I2C(scl=machine.Pin(5), sda=machine.Pin(4))
address = 24
temp_reg = 0x5
client = MQTTClient(CLIENT_ID, net_config.MQTT_SERVER, net_config.MQTT_PORT)


def startup():
    pass


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
            temp = b"%.1f" % temp_c(temp)
        except OSError as err:
            print("Cannot read sensor:", err)

        print(temp)

        try:
            client.publish(STATE_TOPIC, temp)
        except OSError as err:
            print("Cannot send to mqtt:", err)

        try:
            post_points(config.NODE_LOCATION, { 'temperature' : temp })
        except OSError as err:
            print("Cannot submit data to influx:", err)

        next_update += 30 


def setup():
    global next_update

    startup()

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(net_config.WIFI_SSID, net_config.WIFI_PASSWORD)
    print("connecting to wifi....")
    while not sta_if.isconnected():
        sleep(1)

    print("Connected with IP", sta_if.ifconfig()[0])

    client.connect()
    client.publish(DISCOVER_TOPIC, 
        json.dumps({
            "state_topic": STATE_TOPIC,
            "name" : config.NODE_NAME
        }))

    next_update = time()

if __name__ == "__main__":
    setup()
    while True:
        loop()
