import abc
import sys
import socket
import json
import math
from random import random, randint
from math import fmod
from time import sleep, time
from neopixel import *
import paho.mqtt.client as mqtt
from colorsys import hsv_to_rgb

import net_config
import config
import gradient

CH0_LED_PIN = 21
CH1_LED_PIN = 13
NUM_LEDS = 144 
WHITE = (77, 52, 25) # consumes about 1.08A @5V for each strip

CLIENT_ID = socket.gethostname()
DISCOVER_TOPIC = "homeassistant/light/%s/config" % config.NODE_ID
COMMAND_TOPIC = "home/%s/set" % config.NODE_ID
STATE_TOPIC = "home/%s/state" % config.NODE_ID
BRIGHTNESS_TOPIC = "home/%s/brightness" % config.NODE_ID
RGB_COLOR_TOPIC = "home/%s/rgb" % config.NODE_ID
EFFECT_TOPIC = "home/%s/effect" % config.NODE_ID

CHANNEL_0     = 0
CHANNEL_1     = 1
CHANNEL_BOTH  = 2

class Effect(object):

    def __init__(self, led_art):
        self.led_art = led_art
        self.effect_name = None 

    @property
    def name(self):
        return self.effect_name

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def loop(self):
        pass


class UndulatingEffect(Effect):

    def __init__(self, led_art):
        Effect.__init__(self, led_art)
        self.effect_name = "undulating colors"


    def setup(self):
        self.uoap_index = 0
        self.uaop_steps = 25
        self.uoap_increment = 1.0 / self.uaop_steps 


    def loop(self):
        t = self.uoap_index * 2 * math.pi
        jitter = math.sin(t) / 4
        p = [ (0.0, (255, 0, 255)), 
              (0.45 + jitter, (255, 60, 0)),
              (0.65 + jitter, (255, 60, 0)),
              (1.0, (255, 0, 255))
        ]
        g = gradient.Gradient(NUM_LEDS, p)
        g.render(self.led_art.strips[0])

        p = [ (0.0, (255, 0, 255)), 
              (0.45 - jitter, (255, 60, 0)),
              (0.65 - jitter, (255, 60, 0)),
              (1.0, (255, 0, 255))
        ]
        g = gradient.Gradient(NUM_LEDS, p)
        g.render(self.led_art.strips[1])

        self.led_art.show()

        self.uoap_index += self.uoap_increment
        if self.uoap_index > 1.0:
            self.uoap_index = 0.0



class SolidEffect(Effect):

    def __init__(self, led_art):
        Effect.__init__(self, led_art)
        self.color = (255, 255, 255)
        self.done = False
        self.effect_name = "solid color"


    def setup(self):
        self.done = False


    def set_color(self, color):
        self.color = color
        self.done = False


    def loop(self):
        if not self.done:
            print("set color")
            self.led_art.set_color(self.color)
            self.led_art.show()

        self.done = True


class SparkleEffect(Effect):

    def __init__(self, led_art):
        Effect.__init__(self, led_art)
        self.effect_name = "sparkle"
        self.FADE_CONSTANT = .65
        self.PASSES = 35
        self.DOTS = 10

    def setup(self):
        self.passes = 0
        self.dots = 0

    @staticmethod
    def make_hsv(hue):
        (red, green, blue) = hsv_to_rgb(hue, 1.0, 1.0)
        return (int(red*255), int(green*255), int(blue*266))
    

    @staticmethod
    def create_complementary_palette():
        r = random() / 2.0
        return (SparkleEffect.make_hsv(r), SparkleEffect.make_hsv(fmod(r + .5, 1.0)))


    @staticmethod
    def create_triad_palette():
        r = random() / 3.0
        return (SparkleEffect.make_hsv(r), SparkleEffect.make_hsv(fmod(r + .333, 1.0)), SparkleEffect.make_hsv(fmod(r + .666, 1.0)))


    @staticmethod
    def create_analogous_palette():
        r = random() / 2.0
        s = random() / 8.0
        return (SparkleEffect.make_hsv(r),
                SparkleEffect.make_hsv(fmod(r - s + 1.0, 1.0)),
                SparkleEffect.make_hsv(fmod(r - (s * 2) + 1.0, 1.0)),
                SparkleEffect.make_hsv(fmod(r + s, 1.0)),
                SparkleEffect.make_hsv(fmod(r + (s * 2), 1.0)))

    def loop(self):

        palette_funcs = (SparkleEffect.create_analogous_palette, SparkleEffect.create_complementary_palette, 
            SparkleEffect.create_triad_palette, SparkleEffect.create_analogous_palette)
        palette = palette_funcs[randint(0, len(palette_funcs) - 1)]()

        for pss in range(self.PASSES):
            for dot in range(self.DOTS):
                for j in range(len(self.led_art.strips)):
                    self.led_art.set_led_color(randint(0, NUM_LEDS-1), palette[randint(0, len(palette)-1)], j)

            self.led_art.show()
            for s in range(10):
                sleep(.05)

            for strip in self.led_art.strips:
                for i in range(NUM_LEDS):
                    color = strip.getPixelColor(i)
                    color = [color >> 16, (color >> 8) & 0xFF, color & 0xFF]
                    for j in range(3):
                        color[j] = int(float(color[j]) * self.FADE_CONSTANT)
                    strip.setPixelColor(i, Color(color[0], color[1], color[2]))



class LEDArt(object):


    def __init__(self):
        self.state = False
        self.brightness = 128
        self.effect_list = []
        self.current_effect = None

        self.strips = [ Adafruit_NeoPixel(NUM_LEDS, CH0_LED_PIN, 700000, 10, False, 255, 0),
                        Adafruit_NeoPixel(NUM_LEDS, CH1_LED_PIN, 700000, 10, False, 255, 1) ]
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
            sleep(.02)


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
            self.set_led_color(randint(0, NUM_LEDS-1), colors[randint(0, 1)], 0)
            self.set_led_color(randint(0, NUM_LEDS-1), colors[randint(0, 1)], 1)
            self.show()
            sleep(.002)

        self.fade_out()
        self.clear()


    @staticmethod
    def on_message(mqttc, user_data, msg):
        mqttc.__led._handle_message(mqttc, msg)


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
                mqttc.publish(STATE_TOPIC, "OFF")
                clear()
                return

            return

        if msg.topic == BRIGHTNESS_TOPIC:
            try:
                self.set_brightness(int(msg.payload))
            except ValueError:
                pass
  
        if msg.topic == EFFECT_TOPIC:
            try:
                self.set_effect(str(msg.payload, 'utf-8'))
            except ValueError:
                pass
        
        if msg.topic == RGB_COLOR_TOPIC:
            r,g,b = payload.split(",")
            if self.current_effect.name == "solid color":
                print("set color")
                self.current_effect.set_color((int(r),int(g),int(b)))

            return
           

    def setup(self):
        self.startup()
        self.set_brightness(self.brightness)

        effect_name_list = []
        for effect in self.effect_list:
            effect_name_list.append(effect.name)

        self.mqttc = mqtt.Client(CLIENT_ID)
        self.mqttc.on_message = LEDArt.on_message
        self.mqttc.connect("10.1.1.2", 1883, 60)
        self.mqttc.loop_start()
        self.mqttc.__led = self

        self.mqttc.subscribe(COMMAND_TOPIC)
        self.mqttc.subscribe(BRIGHTNESS_TOPIC)
        self.mqttc.subscribe(EFFECT_TOPIC)
        self.mqttc.subscribe(RGB_COLOR_TOPIC)
        self.mqttc.publish(DISCOVER_TOPIC, bytes(json.dumps(
            {
                "name": config.NODE_NAME, 
                "command_topic": COMMAND_TOPIC, 
                "state_topic": STATE_TOPIC, 
                "device_class": "light",
                "assumed_state": "true",
                "brightness" : "true",
                "brightness_command_topic": BRIGHTNESS_TOPIC,
                "effect" : "true",
                "effect_command_topic": EFFECT_TOPIC,
                "effect_list": effect_name_list,
                "rgb_color" : "true",
                "rgb_command_topic" : RGB_COLOR_TOPIC,
            }), "utf-8"))



    def loop(self):

        if not self.state:
            return

        if not self.current_effect:
            return

        self.current_effect.loop()
        if not self.state:
            self.fade_out()
            return



if __name__ == "__main__":
    a = LEDArt()
    a.add_effect(SolidEffect(a))
    a.add_effect(UndulatingEffect(a))
    a.add_effect(SparkleEffect(a))
    a.setup()
    try:
        while True:
            a.loop()
    except KeyboardInterrupt:
        a.fade_out()
        a.mqttc.publish(DISCOVER_TOPIC, "")
        a.mqttc.disconnect()
        a.mqttc.loop_stop()
