from math import fmod
from time import sleep, time
import ubinascii
import machine
import dht
import network
import json
from umqtt.simple import MQTTClient
import net_config
import _config as config
from influx import post_points

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
STATE_TOPIC_TEMP = b"home/%s-temp/state" % config.NODE_ID
STATE_TOPIC_HUM = b"home/%s-hum/state" % config.NODE_ID
DISCOVER_TOPIC_TEMP = b"homeassistant/sensor/%s-temp/config" % config.NODE_ID
DISCOVER_TOPIC_HUM = b"homeassistant/sensor/%s-hum/config" % config.NODE_ID

sensor  = dht.DHT11(machine.Pin(2))
client = MQTTClient(CLIENT_ID, net_config.MQTT_SERVER, net_config.MQTT_PORT)

def startup():
    pass


def handle_message(topic, msg):

    print(topic, msg)

    if topic != STATE_TOPIC:
        return


next_update = 0
def loop():
    global next_update

    if next_update and next_update < time():
        next_update += 30 

        try:
            sensor.measure()
        except OSError as err:
            print("Cannot read sensor:", err)
            return

        try:
            post_points(config.NODE_LOCATION, { 'temperature' : sensor.temperature() })
        except OSError as err:
            print("Cannot submit data to influx:", err)

        print("%dC %d%%" % (sensor.temperature(), sensor.humidity()))
        client.publish(STATE_TOPIC_TEMP, b"%d" % sensor.temperature())
        client.publish(STATE_TOPIC_HUM, b"%d" % sensor.humidity())


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

    client.set_callback(handle_message)
    client.connect()
    client.publish(DISCOVER_TOPIC_TEMP, 
        json.dumps({
            "name": config.NODE_NAME_TEMP, 
            "state_topic": STATE_TOPIC_TEMP,
            "unit_of_measurement": "C"
        }))
    client.publish(DISCOVER_TOPIC_HUM, 
        json.dumps({
            "name": config.NODE_NAME_HUM, 
            "state_topic": STATE_TOPIC_HUM,
            "unit_of_measurement": "%"
        }))

    next_update = time()

if __name__ == "__main__":
    setup()
    while True:
        loop()
