from neopixel import Color
import config
import random
import palette
import effect


class SparkleEffect(effect.Effect):

    def __init__(self, led_art):
        effect.Effect.__init__(self, led_art)
        self.effect_name = "sparkle"
        self.FADE_CONSTANT = .65
        self.PASSES = 35
        self.DOTS = 10


    def setup(self):
        self.passes = 0
        self.dots = 0


    def set_color(self, color):
        pass


    @staticmethod
    def create_analogous_palette():
        r = random() / 2.0
        s = random() / 8.0
        return (palette.make_hsv(r),
                palette.make_hsv(fmod(r - s + 1.0, 1.0)),
                palette.make_hsv(fmod(r - (s * 2) + 1.0, 1.0)),
                palette.make_hsv(fmod(r + s, 1.0)),
                palette.make_hsv(fmod(r + (s * 2), 1.0)))


    def loop(self):

        pal = palette.create_random_palette()
        for pss in range(self.PASSES):
            for dot in range(self.DOTS):
                for j in range(len(self.led_art.strips)):
                    self.led_art.set_led_color(randint(0, config.NUM_LEDS-1), pal[randint(0, len(pal)-1)], j)

            self.led_art.show()
            for s in range(10):
                sleep(.05)

            for strip in self.led_art.strips:
                for i in range(config.NUM_LEDS):
                    color = strip.getPixelColor(i)
                    color = [color >> 16, (color >> 8) & 0xFF, color & 0xFF]
                    for j in range(3):
                        color[j] = int(float(color[j]) * self.FADE_CONSTANT)
                    strip.setPixelColor(i, Color(color[0], color[1], color[2]))
