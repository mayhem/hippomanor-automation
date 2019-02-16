from math import pi, sin
from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv

import config
import gradient
import palette
import effect
from rpi_led_strip import CHANNEL_0, CHANNEL_1


class UndulatingEffect(effect.Effect):

    def __init__(self, led_art, name):
        effect.Effect.__init__(self, led_art, name)
        self.colors = [(255, 0, 255), (255, 60, 0)]


    def setup(self):
        self.color_index = 0
        self.uoap_index = 0
        self.uaop_steps = 25
        self.uoap_increment = 1.0 / self.uaop_steps 


    def set_color(self, color):
        if color in self.colors:
            return

        self.colors[self.color_index] = color
        self.color_index = (self.color_index + 1) % 2


    def loop(self):
        t = self.uoap_index * 2 * pi
        jitter = sin(t) / 4
        p = [ (0.0, self.colors[0]), 
              (0.45 + jitter, self.colors[1]),
              (0.65 + jitter, self.colors[1]),
              (1.0, self.colors[0])
        ]
        g = gradient.Gradient(config.NUM_LEDS, p)
        g.render(self.led_art, CHANNEL_0)

        p = [ (0.0, self.colors[0]), 
              (0.65 - jitter, self.colors[1]),
              (0.45 - jitter, self.colors[1]),
              (1.0, self.colors[0])
        ]
        g = gradient.Gradient(config.NUM_LEDS, p)
        g.render(self.led_art, CHANNEL_1)

        self.led_art.show()

        self.uoap_index += self.uoap_increment
        if self.uoap_index > 1.0:
            self.uoap_index = 0.0
