from neopixel import Color
from time import sleep
import config
from random import random, randint
import palette
import effect
from math import fmod


class SparkleEffect(effect.Effect):

    NAME = "sparkle"

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)
        self.FADE_CONSTANT = .85
        self.DOTS = 20
        self.hue = random()

    def setup(self):
        self.pal = self.create_analogous_palette()

    def set_color(self, color):
        pass

    def nudge(self):
        self.hue += .1 + (random() * .1)
        self.pal = self.create_analogous_palette()

    def create_analogous_palette(self):
        jitter = .01 + (random() / 64) 
        return (palette.make_hsv(self.hue),
                palette.make_hsv(fmod(self.hue - jitter + 1.0, 1.0)),
                palette.make_hsv(fmod(self.hue - (jitter * 2) + 1.0, 1.0)),
                palette.make_hsv(fmod(self.hue + jitter, 1.0)),
                palette.make_hsv(fmod(self.hue + (jitter * 2), 1.0)))

    def loop(self):

        for strip in self.led_art.strips:
            for i in range(config.NUM_LEDS):
                color = strip.getPixelColor(i)
                color = [color >> 16, (color >> 8) & 0xFF, color & 0xFF]
                for j in range(3):
                    color[j] = int(float(color[j]) * self.FADE_CONSTANT)
                strip.setPixelColor(i, Color(color[0], color[1], color[2]))

            for dot in range(self.DOTS):
                strip.setPixelColor(randint(0, config.NUM_LEDS-1), Color(*self.pal[randint(0, len(self.pal)-1)]))

        self.led_art.show()
        sleep(.3)
