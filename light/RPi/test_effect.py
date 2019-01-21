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


class TestEffect(effect.Effect):

    def __init__(self, led_art, name):
        effect.Effect.__init__(self, led_art, name)
        self.palette = []
        self.render_increment = .005
        self.direction = 1


    def fill_source(self):
        base_source = list(palette.create_random_palette())
        print(base_source)
        for i in range(6):
            self.source.extend(base_source)


    def setup(self):
        self.source = []
        self.palette = []

        self.fill_source()
        self.point_distance = 1.0 / len(self.source)
        for i in range(len(self.source)):
            self.palette.append( [ self.point_distance * i , self.source.pop(0) ] )

        self.fill_source()


    def set_color(self, color):
        self.source = palette.create_triad_palette(color)
        self.source_index = 0


    def move_points(self, increment):
        # Move all the points down a smidge
        for i in range(len(self.palette)):
            self.palette[i] = [ self.palette[i][0] + increment, self.palette[i][1] ]


    def print_palette(self, palette):

        for d, color in palette:
            print("%.4f (%d, %d, %d)" % (d, color[0], color[1], color[2]))
        print()


    def loop(self):

        try:
            g = gradient.Gradient(config.NUM_LEDS, self.palette)
            g.render(self.led_art) 
            self.led_art.show()
        except ValueError as err:
            pass

        if self.direction:
            self.move_points(self.render_increment)
            if self.palette[0][0] > 0.0:
                self.palette.insert(0, [ self.palette[0][0] - self.point_distance, self.source.pop(0)])
            try:
                while self.palette[-2][0] > 1.0:
                    self.palette.pop()
            except IndexError:
                pass
        else:
            self.move_points(-self.render_increment)
            if self.palette[-1][0] < 1.0:
                self.palette.append([self.palette[-1][0] + self.point_distance, self.source.pop(0)])
            try:
                while self.palette[1][0] < 0.0:
                    self.palette.pop(0)
            except IndexError:
                pass

        if not self.source:
            self.fill_source()

        sleep(.01)
