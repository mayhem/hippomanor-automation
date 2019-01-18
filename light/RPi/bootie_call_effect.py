from random import random
from math import sin, pi
from time import sleep
from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv
from gamma import GAMMA_TABLE

import palette
import effect


class BootieCallEffect(effect.Effect):

    def __init__(self, led_art, name, value_increment = .01, gamma_correct = False):
        effect.Effect.__init__(self, led_art, name)
        self.gamma_correct = gamma_correct
        self.value_increment = value_increment


    def setup(self):
        self.hue = 0.0
        self.value = 0.0
        self.next_color = None


    def set_color(self, color):
        self.next_color = color


    def loop(self):

        value = (sin(self.value * pi * 2.0) + 1.0) / 6.0
        color = palette.make_hsv(self.hue, 1.0, value)

        if self.gamma_correct:
            color = (GAMMA_TABLE[color[0]], GAMMA_TABLE[color[1]], GAMMA_TABLE[color[2]])

        self.led_art.set_color(color)
        self.led_art.show()
        sleep(.001)

        if value < .0000001:
            if not self.next_color:
                self.hue = random()
            else:
                self.hue, s, v = rgb_to_hsv(float(self.next_color[0]) / 255, 
                       float(self.next_color[1]) / 255,
                       float(self.next_color[2]) / 255)
                self.next_color = None

        self.value += self.value_increment
