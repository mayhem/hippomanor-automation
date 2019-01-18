import math
from random import random, randint, seed
from math import fmod, sin, pi
from time import sleep, time
from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv
import undulating_effect

import config
import gradient
import palette
import effect


class ColorCycleEffect(effect.Effect):

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art)
        self.effect_name = "color cycling"
        self.palette = []
        self.point_distance = .25
        self.render_increment = .01


    def setup(self):

        self.source = list(palette.create_random_palette())
        self.source_index = 0
        self.num_new_points = 0
        self.palette = []
        for i in range(len(self.source) + 1):
            self.palette.append( [ float(i) / len(self.source), self.source[self.source_index] ] )
            self.source_index = (self.source_index + 1) % len(self.source)

    def set_color(self, color):
        self.source = palette.create_triad_palette(color)
        self.source_index = 0


    def loop(self):

        try:
            g = gradient.Gradient(config.NUM_LEDS, self.palette)
            g.render(self.led_art.strips[0])
            g.render(self.led_art.strips[1])
            self.led_art.show()
        except ValueError as err:
            pass

        # Move all the points down a smidge
        for i in range(len(self.palette)):
            self.palette[i] = [ self.palette[i][0] + self.render_increment, self.palette[i][1] ]

        # Has my closest point gone over 0.0? Time to insert a new point!
        if self.palette[0][0] > 0.0:
            self.palette.insert(0, [ self.palette[0][0] - self.point_distance, self.source[self.source_index]])
            self.source_index = (self.source_index + 1) % len(self.source)
        
            if not self.source:
                self.source = list(palette.create_random_palette())

            # clean up the point(s) that went out the other end
            try:
                while self.palette[-2][0] > 1.0:
                    self.palette.pop()
            except IndexError:
                pass

            if self.num_new_points == 10:
                self.source = list(palette.create_random_palette())
                self.source_index = 0
                self.num_new_points = 0

            self.num_new_points += 1

        sleep(.03)
