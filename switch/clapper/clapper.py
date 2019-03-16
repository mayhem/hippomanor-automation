from math import fmod, fabs
from utime import sleep_ms as sleep, ticks_ms as ticks
import ubinascii
import machine
import network
import json
from umqtt.simple import MQTTClient
from machine import I2C
from neopixel import NeoPixel
import net_config
import _config as config

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
# modified
COMMAND_TOPIC = b"lips/command"
#COMMAND_TOPIC = b"home/%s/set" % config.NODE_ID
STATE_TOPIC = b"home/%s/state" % config.NODE_ID
DISCOVER_TOPIC = b"homeassistant/switch/%s/config" % config.NODE_ID
REDISCOVER_TOPIC = b"rediscover"
LED_PIN = 14

# Global object handle
cl = None

def handle_message(topic, msg):
    cl.handle_message(topic, msg)


class ServiceObject(object):

    FUCK_IT_DROP_EVERYTHING = 850 

    def __init__(self):
        self.client = MQTTClient(CLIENT_ID, net_config.MQTT_SERVER, net_config.MQTT_PORT)
        self.np = NeoPixel(machine.Pin(LED_PIN, machine.Pin.OUT), 1)
        self.sensor_total = 0
        self.sensor_count = 0
        self.sensor_floor = 0 
        self.train_count = 0

        self.led_off_time = 0
        self.cool_off_time = 0

        self.buffer = []
        self.buffer_size = 6 # samples

        self.peaks = []
        self.states = [ False, False ]


    def handle_message(self, topic, msg):
        pass
#        if topic == REDISCOVER_TOPIC:
#            self.send_discover_msg()


    def add_or_replace_sample(self, value):
        self.buffer.append(value)
        while len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)


    def calculate_buffer_stats(self):
        """ Returns a tuple (total energy, avg energy) """
        total = 0
        for sample in self.buffer:
            total += sample

        return (total, float(total) / len(self.buffer))


    def set_color(self, red, green, blue):
        self.np[0] = (red, green, blue)
        self.np.write() 


    def clear(self):
        self.set_color(0,0,0)


    def clear_state(self):
        self.peaks = []
        self.set_color(2, 2, 2)
        sleep(25)
        self.clear()
        sleep(150)
        self.clear()

    def send_discover_msg(self):
        self.client.publish(DISCOVER_TOPIC, 
            json.dumps({
                "command_topic": COMMAND_TOPIC,
                "name" : config.NODE_NAME,
            }))


    def setup(self):

        for i in range(5):
            self.set_color(128, 60, 0)
            sleep(100)
            self.set_color(128, 0, 128)
            sleep(100)

        self.clear()

        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(False)
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(net_config.WIFI_SSID, net_config.WIFI_PASSWORD)
        print("connecting to wifi....")
        led = 0
        while not sta_if.isconnected():
            if led:
                self.set_color(16, 0, 16)
            else:
                self.clear()
            led = not led
            sleep(200)

        print("Connected with IP", sta_if.ifconfig()[0])
        self.clear()

        self.client.set_callback(handle_message)
        self.client.connect()
#        self.send_discover_msg()



    def loop(self):
        if ticks() >= self.led_off_time:
            self.led_off_time = 0
            self.clear()

        if ticks() < self.cool_off_time:
            return

        try:
            sensor_value = machine.ADC(0).read()
        except OSError as err:
            print("Cannot read sensor:", err)
            return

        self.sensor_total += sensor_value
        self.sensor_count += 1

        if self.sensor_count == 1000:
            self.sensor_floor = self.sensor_total / self.sensor_count
            #print("F ", self.sensor_floor)
            self.sensor_count = 0
            self.sensor_total = 0
        
        if self.sensor_floor == 0:
            return

        sensor_value = sensor_value - self.sensor_floor
        self.add_or_replace_sample(sensor_value)

        total, avg = self.calculate_buffer_stats()
        if total > 10:
            self.peaks.append(ticks())

            if len(self.peaks) == 1:
                self.set_color(16, 0, 0)
            elif len(self.peaks) == 2:
                self.set_color(0, 16, 0)
            elif len(self.peaks) == 3:
                self.set_color(0, 0, 16)
            else:
                self.clear_state()
                return

            self.buffer = []
            sleep(150)
            self.clear()

        if self.peaks:
            # check for the clock wrapping round
            if self.peaks[-1] > ticks():
                print("Clock wrap detected!")
                self.peaks = []
                self.clear()

            if self.peaks[-1] + self.FUCK_IT_DROP_EVERYTHING <= ticks():

                if len(self.peaks) == 2:
                    self.states[0] = not self.states[0]
                    self.client.publish(COMMAND_TOPIC, "TOGGLE")

                if len(self.peaks) == 3:
                    self.client.publish(COMMAND_TOPIC, "MODE")

                self.clear_state()




if __name__ == "__main__":
    cl = ServiceObject()
    cl.setup()
    while True:
        cl.loop()
