from colorsys import hsv_to_rgb
from math import fabs
import os

from neopixel import Color

class Gradient(object):

    def __init__(self, num_leds, palette):

        self.FENCEPOST_TOLERANCE = .0001

        # palletes are in format [ (.345, (128, 0, 128)) ]
        self._validate_palette(palette)
        self.palette = palette
        self.num_leds = num_leds


    def _validate_palette(self, palette):

        if len(palette) < 2:
            raise ValueError("Palette must have at least two points.")

        if palette[0][0] > 0.0:
            raise ValueError("First point in palette must be less than or equal to 0.0")

        if palette[-1][0] < 1.0:
            raise ValueError("Last point in palette must be greater than or equal to 1.0")



    def render(self, strip):

        for led in range(self.num_leds):
            led_offset = float(led) / float(self.num_leds - 1)
            for index in range(len(self.palette)):

                # skip the first item
                if index == 0:
                    continue

                if self.palette[index][0] >= led_offset:
                    section_begin_offset = self.palette[index-1][0]
                    section_end_offset = self.palette[index][0]

                    percent = (led_offset - section_begin_offset) / (section_end_offset - section_begin_offset)
                    new_color = []
                    for color in range(3):
                        new_color.append(int(self.palette[index-1][1][color] + 
                                ((self.palette[index][1][color] - self.palette[index-1][1][color]) * percent)))

                    strip.setPixelColor(led, Color(min(new_color[1], 255), min(new_color[0], 255), min(new_color[2], 255)))
                    break

