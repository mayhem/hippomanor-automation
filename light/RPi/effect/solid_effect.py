from math import fmod
from random import random
import palette
import effect


class SolidEffect(effect.Effect):

    NAME = "solid"

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)
        self.hue = random()
        self.nudge()

    def nudge(self):
        self.hue += fmod(.1 + (random() * .1), 1.0)
        self.color = palette.make_hsv(self.hue)

    def set_color(self, color):
        self.color = color

    def loop(self):
        self.led_art.set_color(self.color)
        self.led_art.show()
