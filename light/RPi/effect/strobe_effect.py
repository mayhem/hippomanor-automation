from random import random
from math import sin, pi
from time import sleep, time

import effect
import palette


class StrobeEffect(effect.Effect):

    def __init__(self, led_art, name, period, hue_increment):
        effect.Effect.__init__(self, led_art, name)
        self.period = period
        self.update_interval = 1.0 / period
        self.hue_increment = hue_increment
        self.hue = 0.0

        self.color = (0,0,0)
        self.state = 0


    def setup(self):
        self.next_update = time()


    def set_color(self, color):
        pass


    def loop(self):

        if time() > self.next_update:
            self.next_update += self.update_interval

            if self.state:
                color = (0,0,0)
            else:
                color = palette.make_hsv(self.hue, 1.0, .5 + (random()/2.0))

            self.state = not self.state
            self.led_art.set_color(color)
            self.led_art.show()

            self.hue += self.hue_increment

        sleep(.01)
