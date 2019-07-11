from random import random, randint, seed, uniform
from math import fmod, sin, pi, cos
from time import sleep, time
from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv

import config
import gradient
import palette
import effect


class TestEffect(effect.Effect):

    NAME = "test"
    POINTS = 16

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art, self.NAME)


    def _get_next_color(self):
        if not self.source or not len(self.source):
            self.source = list(palette.create_analogous_palette())

        return self.source.pop(0)


    def setup(self):
        self.palette = []
        self.source = []
        self.scale = 1.0
        self.offset = 0.0
        self.t = 0

        point_distance = 1.0 / self.POINTS
        for i in range(self.POINTS):
            self.palette.append( [ point_distance * i , self._get_next_color() ] )

        self.palette.append( [ point_distance * self.POINTS , self.palette[0][1] ] )
        self.print_palette(self.palette)


    def set_color(self, color):
        pass

    def print_palette(self, palette):
        for i, pal in enumerate(palette):
            print("%d %.4f (%d, %d, %d)" % (i, pal[0], pal[1][0], pal[1][1], pal[1][2]))
        print()


    def loop(self):

        try:
            g = gradient.Gradient(config.NUM_LEDS, self.palette)
            g.set_scale(self.scale)
            g.set_offset(self.offset)
            g.render(self.led_art, 2) 
            self.led_art.show()
        except ValueError as err:
            print(err) 
            pass

        self.t += .08
        self.scale = 2.0 + (sin(self.t) / 1.0)
        self.offset = .5 + (cos(self.t) / 4.0)
#        print("%.3f %.3f" % (self.offset, self.scale)) 

        sleep(.005)
