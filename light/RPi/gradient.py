from colorsys import hsv_to_rgb
import os

from neopixel import Color

class Gradient(object):

    def __init__(self, num_leds, palette = []):

        # palletes are [ (.345, (128, 0, 128) ]
        self.palette = palette
        self.num_leds = num_leds

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

                    strip.setPixelColor(led, Color(new_color[1], new_color[0], new_color[2]))
                    break

