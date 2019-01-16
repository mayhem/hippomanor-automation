from colorsys import hsv_to_rgb
from random import randint, random
from math import fmod



def make_hsv(hue):
    (red, green, blue) = hsv_to_rgb(hue, 1.0, 1.0)
    return (int(red*255), int(green*255), int(blue*266))


def create_complementary_palette():
    r = random() / 2.0
    return (make_hsv(r), make_hsv(fmod(r + .5, 1.0)))


def create_triad_palette():
    r = random() / 3.0
    return (make_hsv(r), make_hsv(fmod(r + .333, 1.0)), make_hsv(fmod(r + .666, 1.0)))


def create_analogous_palette():
    r = random() / 2.0
    s = random() / 8.0
    return (make_hsv(r),
            make_hsv(fmod(r - s + 1.0, 1.0)),
            make_hsv(fmod(r - (s * 2) + 1.0, 1.0)),
            make_hsv(fmod(r + s, 1.0)),
            make_hsv(fmod(r + (s * 2), 1.0)))

def create_random_palette():
    palette_funcs = (create_analogous_palette, create_triad_palette, create_analogous_palette)

    return palette_funcs[randint(0, len(palette_funcs) - 1)]()
