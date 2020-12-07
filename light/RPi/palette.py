from colorsys import hsv_to_rgb, rgb_to_hsv
from random import randint, random, uniform
from math import fmod

from gradient import Gradient


def make_hsv(hue, saturation = 1.0, value = 1.0):
    (red, green, blue) = hsv_to_rgb(hue, saturation, value)
    return (int(red*255), int(green*255), int(blue*266))


def create_complementary_palette():
    r = random() / 2.0
    return (make_hsv(r), make_hsv(fmod(r + .5, 1.0)))


def create_triad_palette(color = None):
    if not color:
        r = random() / 3.0
    else:
        r, s, v = rgb_to_hsv(float(color[0]) / 255, 
               float(color[1]) / 255,
               float(color[2]) / 255)

    return (make_hsv(r), make_hsv(fmod(r + .333, 1.0)), make_hsv(fmod(r + .666, 1.0)))


def create_analogous_palette(scale = 10.0, offset = 0.04):
    r = random()
    s = (random() / scale) + offset
    return (make_hsv(r),
            make_hsv(fmod(r - s + 1.0, 1.0)),
            make_hsv(fmod(r - (s * 2) + 1.0, 1.0)),
            make_hsv(fmod(r + s, 1.0)),
            make_hsv(fmod(r + (s * 2), 1.0)))


def create_sleepy_analogous_palette(scale = 10.0, offset = 0.04):
    begin = uniform(.00, .14)
    end = uniform(.17, .33)
    step = (end - begin) / 4
    pal = [
        make_hsv(begin),
        make_hsv(begin + step),
        make_hsv(begin + step + step),
        make_hsv(end)]

    for i, p in enumerate(pal):
        pal[i] = (pal[i][0], pal[i][1], 0)

    return pal


def create_random_palette():
    palette_funcs = (create_analogous_palette, create_triad_palette, create_analogous_palette)

    return palette_funcs[randint(0, len(palette_funcs) - 1)]()


class ColorSchemePalette():

    def __init__(self, color_list):
        dist = 1.0 / (len(color_list) - 1)
        palette = [(i * dist, color) for i, color in enumerate(color_list)]
        self.gradient = Gradient(palette)

    def color(self, index):
        return self.gradient.get_color_by_offset(index)
