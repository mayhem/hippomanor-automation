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



CLIENT_ID = socket.gethostname()
# modified!
COMMAND_TOPIC = "%s/command" % config.NODE_ID
STATE_TOPIC = "%s/state" % config.NODE_ID 
BRIGHTNESS_TOPIC = "%s/brightness" % config.NODE_ID
BRIGHTNESS_STATE_TOPIC = "%s/brightness_state" % config.NODE_ID
COLOR_TOPIC = "%s/color" % config.NODE_ID
COLOR_STATE_TOPIC = "%s/color_state" % config.NODE_ID
EFFECT_TOPIC = "%s/effect" % config.NODE_ID

# Philips dimmer that is connected via zigbee2mqtt
DIMMER_TOPIC = "zigbee2mqtt/0x00178801080a1a7b/action"

CHANNEL_0     = 0
CHANNEL_1     = 1
CHANNEL_BOTH  = 2
INITIAL_BRIGHTNESS = 30

from effect import solid_effect
from effect import sparkle_effect
from effect import undulating_effect
from effect import colorcycle_effect
from effect import bootie_call_effect
from effect import strobe_effect
from effect import test_effect
from effect import chill_bed_time_effect
from effect import dynamic_colorcycle_effect

class Lips(object):


    def __init__(self):
        self.brightness = INITIAL_BRIGHTNESS
        self.last_brightness = INITIAL_BRIGHTNESS
        self.effect_list = []
        self.current_effect = None
        self.current_effect_index = -1

        self.strips = [ Adafruit_NeoPixel(config.NUM_LEDS, config.CH0_LED_PIN, 800000, 10, False, 255, 0),
                        Adafruit_NeoPixel(config.NUM_LEDS, config.CH1_LED_PIN, 800000, 10, False, 255, 1) ]
        for s in self.strips:
            s.begin()

        self.mqttc = None


    def publish(self, topic, payload):
        if not self.mqttc:
            return

        self.mqttc.publish(topic, payload)


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


    def show(self, channel=CHANNEL_BOTH):
        if channel == CHANNEL_0 or channel == CHANNEL_BOTH:
            self.strips[0].show()
        if channel == CHANNEL_1 or channel == CHANNEL_BOTH:
            self.strips[1].show()


    def clear(self, channel=CHANNEL_BOTH):
        self.set_color((0,0,0), channel)
        self.show(channel)


    def turn_on(self):
        if self.brightness == 0:
            print("read last brightness: %d" % (self.brightness))
            self.brightness = self.last_brightness
            print("turn on. brightness: %d" % self.brightness)
            self.publish(STATE_TOPIC, "1")
            self.publish(BRIGHTNESS_STATE_TOPIC, "%d" % self.brightness)
        else:
            print("already on")


    def turn_off(self):
        if self.brightness:
            self.last_brightness = self.brightness
            print("set last brightness: %d" % (self.brightness))
            while self.brightness > 0:
                self.set_brightness(self.brightness - 5)
                print("off: %d" % self.brightness)

            self.set_brightness(0)
            self.clear()

            print("turn off.")
            self.publish(STATE_TOPIC, "0")
            self.publish(BRIGHTNESS_STATE_TOPIC, "%d" % self.brightness)
        else:
            print("already off")


    def set_brightness(self, brightness):

        if brightness < 0:
            brightness = 0
        elif brightness > 100:
            brightness = 100

        if self.brightness and brightness == 0:
            self.publish(STATE_TOPIC, "0")

        if brightness:
            for strip in self.strips:
                strip.setBrightness(brightness)
                strip.show()
        else:
            self.clear()

        self.brightness = brightness
        self.publish(BRIGHTNESS_STATE_TOPIC, "%d" % brightness)


    def brightness_up(self):
        if self.brightness == 100:
            return

        if not self.brightness:
            self.set_brightness(10)
        else:
            self.set_brightness(self.brightness + 10)

        print("UP new brightness: %d" % self.brightness)


    def brightness_down(self):
        if not self.brightness:
            return

        if self.brightness <= 10:
            print("set last brightness: %d" % (self.brightness))
            self.last_brightness = self.brightness
            self.set_brightness(0)
            return

        self.set_brightness(self.brightness - 10)
        print("DOWN new brightness: %d" % self.brightness)


    def fade_in(self, target_brightness, channel=CHANNEL_BOTH):
        ''' this assumes that brightness has been set to zero and that a patterns is loaded ready to go '''

        brightness_inc = 10
        while self.brightness + brightness_inc < target_brightness:
            self.set_brightness(self.brightness + brightness_inc)

        self.set_brightness(target_brightness)




    def set_effect(self, effect_name):
        for i, effect in enumerate(self.effect_list):
            if effect.name == effect_name:
                self.turn_off()
                self.current_effect = effect 
                self.current_effect.setup()
                self.current_effect_index = i
                self.turn_on()
                break
        else:
            print("Unknown effect %s" % effect_name)


    def add_effect(self, effect):
        self.effect_list.append(effect)
        if len(self.effect_list) == 1:
            self.set_effect(str(effect.name))


    def next_effect(self):
        index = (self.current_effect_index + 1) % len(self.effect_list)
        self.set_effect(str(self.effect_list[index].name))


    def startup(self):

        colors = ( (128, 0, 128), (128, 30, 0) )

        for p in range(100):
            self.set_led_color(randint(0, config.NUM_LEDS-1), colors[randint(0, 1)], 0)
            self.set_led_color(randint(0, config.NUM_LEDS-1), colors[randint(0, 1)], 1)
            self.show()
            sleep(.002)

        self.turn_off()
        self.clear()


    @staticmethod
    def on_message(mqttc, user_data, msg):
        try:
            mqttc.__led._handle_message(mqttc, msg)
        except Exception as err:
            traceback.print_exc(file=sys.stdout)


    def _handle_message(self, mqttc, msg):

        payload = str(msg.payload, 'utf-8')
        print(msg.topic)
        if msg.topic == COMMAND_TOPIC:
            if msg.payload.lower() == b"mode":
                self.next_effect()
                return

            if msg.payload.lower() == b"on":
                self.turn_on()
                return

            if msg.payload.lower() == b"off":
                self.turn_off()
                return

            if msg.payload.lower() == b"toggle":
                if self.state:
                    self.turn_off()
                    return
                else:
                    self.fade_in()
                    return

            return

        if msg.topic == BRIGHTNESS_TOPIC:
            try:
                self.set_brightness(int(msg.payload))
            except ValueError:
                pass
            return
  
        if msg.topic == EFFECT_TOPIC:
            effect = str(msg.payload, 'utf-8')
            try:
                self.set_effect(effect)
            except ValueError:
                print("Invalid effect: '%s'" % effect)
            return
        
        if msg.topic == COLOR_TOPIC:
            color = (int(msg.payload[1:3], 16),int(msg.payload[3:5], 16),int(msg.payload[5:7], 16))
            self.current_effect.set_color(color)
            self.publish(COLOR_STATE_TOPIC, msg.payload)
            return
           
        if msg.topic == DIMMER_TOPIC:
            action = str(msg.payload, 'utf-8')
            print("===== %s" % action)
            
            if msg.payload.lower() == b"on-press":
                self.turn_on()
                return

            if msg.payload.lower() == b"off-press":
                self.turn_off()
                return

            if msg.payload.lower() == b"up-press":
                self.brightness_up()
                return

            if msg.payload.lower() == b"down-press":
                self.brightness_down()
                return
        

    def setup(self):
        #self.startup()
        self.set_brightness(self.brightness)

        self.mqttc = mqtt.Client(CLIENT_ID)
        self.mqttc.on_message = Lips.on_message
        self.mqttc.connect("10.1.1.2", 1883, 60)
        self.mqttc.loop_start()
        self.mqttc.__led = self

        effect_name_list = []
        for effect in self.effect_list:
            print("adding effect %s" % effect.name)
            effect_name_list.append(effect.name)

        self.mqttc.subscribe(COMMAND_TOPIC)
        self.mqttc.subscribe(BRIGHTNESS_TOPIC)
        self.mqttc.subscribe(EFFECT_TOPIC)
        self.mqttc.subscribe(COLOR_TOPIC)
        self.mqttc.subscribe(DIMMER_TOPIC)


    def loop(self):
        if self.current_effect and self.brightness:
            self.current_effect.loop()


if __name__ == "__main__":
    seed()
    a = Lips()
    a.add_effect(test_effect.TestEffect(a))
    a.add_effect(chill_bed_time_effect.ChillBedTimeEffect(a))
    a.add_effect(dynamic_colorcycle_effect.DynamicColorCycleEffect(a))
    a.add_effect(solid_effect.SolidEffect(a))
    a.add_effect(sparkle_effect.SparkleEffect(a))
    a.add_effect(undulating_effect.UndulatingEffect(a))
    a.add_effect(bootie_call_effect.BootieCallEffect(a, .0005))

    a.setup()
    if config.TURN_ON_AT_START:
        a.turn_on()
    try:
        while True:
            a.loop()
            sleep(.0001)
    except KeyboardInterrupt:
        a.turn_off()
        a.mqttc.disconnect()
        a.mqttc.loop_stop()
