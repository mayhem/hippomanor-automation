import sys
import socket
import json
from random import random, randint
from math import fmod
from time import sleep, time
from neopixel import *
import paho.mqtt.client as mqtt
from colorsys import hsv_to_rgb

import net_config
import config

CH0_LED_PIN = 18
CH1_LED_PIN = 13
NUM_LEDS = 144 
WHITE = (77, 52, 25) # consumes about 1.08A @5V for each strip

CLIENT_ID = socket.gethostname()
COMMAND_TOPIC = "home/%s/set" % config.NODE_ID
STATE_TOPIC = "home/%s/state" % config.NODE_ID
DISCOVER_TOPIC = "homeassistant/light/%s/config" % config.NODE_ID

CHANNEL_0     = 0
CHANNEL_1     = 1
CHANNEL_BOTH  = 2

class LEDArt(object):


    def __init__(self):
        self.state = False
        self.FADE_CONSTANT = .65
        self.PASSES = 35
        self.DOTS = 10

        self.strips = [ Adafruit_NeoPixel(NUM_LEDS, CH0_LED_PIN, 800000, 10, False, 255, 0), 
                        Adafruit_NeoPixel(NUM_LEDS, CH1_LED_PIN, 800000, 10, False, 255, 1) ]
        for s in self.strips:
            s.begin()

        self.mqttc = None

    def set_color(self, col, channel=CHANNEL_BOTH):
        for i in range(NUM_LEDS):
            if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
                self.strips[0].setPixelColor(i, Color(col[1], col[0], col[2]))
            if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
                self.strips[1].setPixelColor(i, Color(col[1], col[0], col[2]))


    def set_led_color(self, led, col, channel=CHANNEL_BOTH):
        if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
            self.strips[0].setPixelColor(led, Color(col[1], col[0], col[2]))
        if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
            self.strips[1].setPixelColor(led, Color(col[1], col[0], col[2]))


    def clear(self, channel=CHANNEL_BOTH):
        self.set_color((0,0,0), channel)
        self.show(channel)


    def fade_out(self, channel=CHANNEL_BOTH):
        for p in range(7):
            for strip in self.strips:
                self._fade_strip(strip, .8)
            self.show()


    def _fade_strip(self, strip, fade):
        for i in range(NUM_LEDS):
            color = strip.getPixelColor(i)
            color = [color >> 16, (color >> 8) & 0xFF, color & 0xFF]
            for j in range(3):
                color[j] >>= 1
            strip.setPixelColor(i, Color(color[0], color[1], color[2]))


    def show(self, channel=CHANNEL_BOTH):
        if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
            self.strips[0].show()
        if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
            self.strips[1].show()


    def startup(self):

        colors = ( (128, 0, 128), (128, 30, 0) )

        self.clear()
        self.clear()
        for p in range(6):
            self.set_color(colors[0], p % 2)
            self.set_color(colors[1], (p+1) % 2)
            self.show()
            sleep(.2)

        self.clear()

    @staticmethod
    def make_hsv(hue):
        (red, green, blue) = hsv_to_rgb(hue, 1.0, 1.0)
        return (int(red*255), int(green*255), int(blue*266))
    

    @staticmethod
    def create_complementary_palette():
        r = random() / 2.0
        return (LEDArt.make_hsv(r), LEDArt.make_hsv(fmod(r + .5, 1.0)))


    @staticmethod
    def create_triad_palette():
        r = random() / 3.0
        return (LEDArt.make_hsv(r), LEDArt.make_hsv(fmod(r + .333, 1.0)), LEDArt.make_hsv(fmod(r + .666, 1.0)))


    @staticmethod
    def create_analogous_palette():
        r = random() / 2.0
        s = random() / 8.0
        return (LEDArt.make_hsv(r),
                LEDArt.make_hsv(fmod(r - s + 1.0, 1.0)),
                LEDArt.make_hsv(fmod(r - (s * 2) + 1.0, 1.0)),
                LEDArt.make_hsv(fmod(r + s, 1.0)),
                LEDArt.make_hsv(fmod(r + (s * 2), 1.0)))


    @staticmethod
    def on_message(mqttc, user_data, msg):
        print("on message", msg.topic, msg.payload)
        mqttc.__led._handle_message(mqttc, msg)


    def _handle_message(self, mqttc, msg):
        if msg.topic != COMMAND_TOPIC:
            return

        if msg.payload.lower() == b"on":
            self.state = True
            mqttc.publish(STATE_TOPIC, "ON")
            return

        if msg.payload.lower() == b"off":
            self.state = False
            mqttc.publish(STATE_TOPIC, "OFF")
            clear()
            return


    def loop(self):

        if not self.state:
            return

        try:
            palette_funcs = (LEDArt.create_analogous_palette, LEDArt.create_complementary_palette, LEDArt.create_triad_palette, LEDArt.create_analogous_palette)
            palette = palette_funcs[randint(0, len(palette_funcs) - 1)]()
            for p in range(self.PASSES):
                for i in range(self.DOTS):
                    for j in range(len(self.strips)):
                        self.set_led_color(randint(0, NUM_LEDS-1), palette[randint(0, len(palette)-1)], j)

                self.show()
                for s in range(10):
                    sleep(.05)

                    if not self.state:
                        self.fade_out()
                        return

                for strip in self.strips:
                    for i in range(NUM_LEDS):
                        color = strip.getPixelColor(i)
                        color = [color >> 16, (color >> 8) & 0xFF, color & 0xFF]
                        for j in range(3):
                            color[j] = int(float(color[j]) * self.FADE_CONSTANT)
                        strip.setPixelColor(i, Color(color[0], color[1], color[2]))

                if not self.state:
                    self.fade_out()
                    return

        except KeyboardInterrupt:
            self.clear()
            self.mqttc.publish(DISCOVER_TOPIC, "")
            self.mqttc.disconnect()
            self.mqttc.loop_stop()
            sys.exit(0)


    def setup(self):
        self.startup()

        self.mqttc = mqtt.Client(CLIENT_ID)
        self.mqttc.on_message = LEDArt.on_message
        self.mqttc.connect("10.1.1.2", 1883, 60)
        self.mqttc.loop_start()
        self.mqttc.__led = self

        self.mqttc.subscribe(COMMAND_TOPIC)
        self.mqttc.publish(DISCOVER_TOPIC, bytes(json.dumps(
            {
                "name": config.NODE_NAME, 
                "command_topic": COMMAND_TOPIC, 
                "device_class": "light",
                "assumed_state": "true"
            }), "utf-8"))

if __name__ == "__main__":
    a = LEDArt()
    a.setup()
    while True:
        a.loop()
