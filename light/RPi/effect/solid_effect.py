from math import fmod
from random import random
import palette
import effect


class SolidEffect(effect.Effect):

    NAME = "solid"

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)
        self.palette = palette.ColorSchemePalette([(255, 0, 0), (255, 160, 0), (255, 255, 0), (255, 0, 255)])
        self.hue = random()
        self.nudge()

    def nudge(self):
        self.hue = fmod(self.hue + .1 + (random() * .05), 1.0)
        self.color = self.palette.color(self.hue)

    def set_color(self, color):
        self.color = color

    def loop(self):
        self.led_art.set_color(self.color)
        self.led_art.show()
