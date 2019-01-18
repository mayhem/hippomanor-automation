from colorsys import hsv_to_rgb, rgb_to_hsv, rgb_to_hsv

import config
import gradient
import palette
import effect


class UndulatingEffect(effect.Effect):

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art)
        self.effect_name = "undulating colors"
        self.colors = [(255, 0, 255), (255, 60, 0)]


    def setup(self):
        self.color_index = 0
        self.uoap_index = 0
        self.uaop_steps = 25
        self.uoap_increment = 1.0 / self.uaop_steps 


    def set_color(self, color):
        self.colors[self.color_index] = color
        self.color_index = (self.color_index + 1) % 2


    def loop(self):
        t = self.uoap_index * 2 * math.pi
        jitter = sin(t) / 4
        p = [ (0.0, self.colors[0]), 
              (0.45 + jitter, self.colors[1]),
              (0.65 + jitter, self.colors[1]),
              (1.0, self.colors[0])
        ]
        g = gradient.Gradient(config.NUM_LEDS, p)
        g.render(self.led_art.strips[0])

        p = [ (0.0, self.colors[0]), 
              (0.45 - jitter, self.colors[1]),
              (0.65 - jitter, self.colors[1]),
              (1.0, self.colors[0])
        ]
        g = gradient.Gradient(config.NUM_LEDS, p)
        g.render(self.led_art.strips[1])

        self.led_art.show()

        self.uoap_index += self.uoap_increment
        if self.uoap_index > 1.0:
            self.uoap_index = 0.0
