import abc
import sys
import socket
import json
import math
import traceback
from random import random, randint, seed
from math import fmod, sin, pi
from time import sleep, time
from neopixel import *
import paho.mqtt.client as mqtt
from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv


import net_config
import config

import solid_effect
import sparkle_effect
import undulating_effect
import colorcycle_effect
import bootie_call_effect
import strobe_effect


CLIENT_ID = socket.gethostname()
DISCOVER_TOPIC = "homeassistant/light/%s/config" % config.NODE_ID
COMMAND_TOPIC = "home/%s/set" % config.NODE_ID
STATE_TOPIC = "home/%s/state" % config.NODE_ID
BRIGHTNESS_TOPIC = "home/%s/brightness" % config.NODE_ID
BRIGHTNESS_STATE_TOPIC = "home/%s/brightness_state" % config.NODE_ID
RGB_COLOR_TOPIC = "home/%s/rgb" % config.NODE_ID
EFFECT_TOPIC = "home/%s/effect" % config.NODE_ID
REDISCOVER_TOPIC = "rediscover"

CHANNEL_0     = 0
CHANNEL_1     = 1
CHANNEL_BOTH  = 2


class LEDArt(object):


    def __init__(self):
        self.state = False
        self.brightness = 128
        self.effect_list = []
        self.current_effect = None

        self.strips = [ Adafruit_NeoPixel(config.NUM_LEDS, config.CH0_LED_PIN, 800000, 10, False, 255, 0),
                        Adafruit_NeoPixel(config.NUM_LEDS, config.CH1_LED_PIN, 800000, 10, False, 255, 1) ]
        for s in self.strips:
            s.begin()

        self.mqttc = None

    def set_color(self, col, channel=CHANNEL_BOTH):
        for i in range(config.NUM_LEDS):
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


    def set_state(self, state):
        self.state = state
        if state:
            self.mqttc.publish(STATE_TOPIC, "ON")
            self.mqttc.publish(BRIGHTNESS_STATE_TOPIC, "%d" % self.brightness)
        else:
            self.mqttc.publish(STATE_TOPIC, "OFF")


    def fade_out(self, channel=CHANNEL_BOTH):
        saved_brightness = self.brightness
        while self.brightness > 0:
            self.set_brightness(max(self.brightness - 10, 0))
            self.show()

        self.clear()
        self.set_brightness(saved_brightness)


    def fade_in(self, target_brightness, channel=CHANNEL_BOTH):
        ''' this assumes that brightness has been set to zero and that a patterns is loaded ready to go '''

        brightness_inc = 10
        while self.brightness + brightness_inc < target_brightness:
            self.set_brightness(self.brightness + brightness_inc)
            self.show()

        self.set_brightness(target_brightness)


    def show(self, channel=CHANNEL_BOTH):
        if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
            self.strips[0].show()
        if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
            self.strips[1].show()


    def set_brightness(self, brightness):
        self.brightness = brightness
        for strip in self.strips:
            strip.setBrightness(brightness)
            strip.show()


    def set_effect(self, effect_name):
        for effect in self.effect_list:
            if effect.name == effect_name:
                saved_state = self.state
                self.state = False
                self.fade_out()
                self.current_effect = effect 
                self.current_effect.setup()
                self.state = saved_state
                break


    def add_effect(self, effect):
        self.effect_list.append(effect)
        if len(self.effect_list) == 1:
            self.set_effect(str(effect.name))


    def startup(self):

        colors = ( (128, 0, 128), (128, 30, 0) )

        for p in range(100):
            self.set_led_color(randint(0, config.NUM_LEDS-1), colors[randint(0, 1)], 0)
            self.set_led_color(randint(0, config.NUM_LEDS-1), colors[randint(0, 1)], 1)
            self.show()
            sleep(.002)

        self.fade_out()
        self.clear()


    @staticmethod
    def on_message(mqttc, user_data, msg):
        try:
            mqttc.__led._handle_message(mqttc, msg)
        except Exception as err:
            traceback.print_exc(file=sys.stdout)


    def _handle_message(self, mqttc, msg):

        payload = str(msg.payload, 'utf-8')
        print("handle %s - %s" % (msg.topic, msg.payload))
        if msg.topic == COMMAND_TOPIC:
            if msg.payload.lower() == b"on":
                self.state = True
                mqttc.publish(STATE_TOPIC, "ON")
                return

            if msg.payload.lower() == b"off":
                self.state = False
                saved = self.brightness
                self.fade_out()
                self.clear()
                self.set_brightness(saved)
                mqttc.publish(STATE_TOPIC, "OFF")
                return

            return

        if msg.topic == BRIGHTNESS_TOPIC:
            try:
                self.set_brightness(int(msg.payload))
            except ValueError:
                pass
            return
  
        if msg.topic == EFFECT_TOPIC:
            try:
                self.set_effect(str(msg.payload, 'utf-8'))
            except ValueError:
                pass
            return
        
        if msg.topic == RGB_COLOR_TOPIC:
            r,g,b = payload.split(",")
            color = (int(r),int(g),int(b))
            self.current_effect.set_color(color)
            return
           
        if msg.topic == REDISCOVER_TOPIC:
            self.send_discover_msg()
            return


    def send_discover_msg(self):

        effect_name_list = []
        for effect in self.effect_list:
            effect_name_list.append(effect.name)

        self.mqttc.publish(DISCOVER_TOPIC, bytes(json.dumps(
            {
                "name": config.NODE_NAME, 
                "command_topic": COMMAND_TOPIC, 
                "state_topic": STATE_TOPIC, 
                "device_class": "light",
                "assumed_state": "true",
                "brightness" : "true",
                "brightness_command_topic": BRIGHTNESS_TOPIC,
#                "brightness_state_topic": BRIGHTNESS_STATE_TOPIC,
                "effect" : "true",
                "effect_command_topic": EFFECT_TOPIC,
                "effect_list": effect_name_list,
                "rgb_color" : "true",
                "rgb_command_topic" : RGB_COLOR_TOPIC,
            }), "utf-8"))


    def setup(self):
        #self.startup()
        self.set_brightness(self.brightness)

        self.mqttc = mqtt.Client(CLIENT_ID)
        self.mqttc.on_message = LEDArt.on_message
        self.mqttc.connect("10.1.1.2", 1883, 60)
        self.mqttc.loop_start()
        self.mqttc.__led = self

        self.mqttc.subscribe(COMMAND_TOPIC)
        self.mqttc.subscribe(BRIGHTNESS_TOPIC)
        self.mqttc.subscribe(EFFECT_TOPIC)
        self.mqttc.subscribe(RGB_COLOR_TOPIC)
        self.mqttc.subscribe(REDISCOVER_TOPIC)
        self.send_discover_msg()



    def loop(self):
        if self.current_effect and self.state:
            self.current_effect.loop()



if __name__ == "__main__":
    seed()
    a = LEDArt()
    a.add_effect(strobe_effect.StrobeEffect(a, "slow strobe", 2, .02))
    a.add_effect(strobe_effect.StrobeEffect(a, "fast strobe", 8, .03))
    a.add_effect(colorcycle_effect.ColorCycleEffect(a, "color cycle"))
    a.add_effect(solid_effect.SolidEffect(a, "solid color"))
    a.add_effect(undulating_effect.UndulatingEffect(a, "undulating colors"))
    a.add_effect(bootie_call_effect.BootieCallEffect(a, "slow bootie call", .0005))
    a.add_effect(bootie_call_effect.BootieCallEffect(a, "fast bootie call", .005))
    a.add_effect(sparkle_effect.SparkleEffect(a, "sparkle"))
    a.setup()
    a.set_state(config.TURN_ON_AT_START)
    try:
        while True:
            a.loop()
    except KeyboardInterrupt:
        a.fade_out()
        a.mqttc.publish(DISCOVER_TOPIC, "")
        a.mqttc.disconnect()
        a.mqttc.loop_stop()
