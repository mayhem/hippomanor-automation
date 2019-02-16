from colorsys import hsv_to_rgb, rgb_to_hsv
from random import randint, random
from math import fmod



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


def create_analogous_palette():
    r = random() / 2.0
    s = (random() / 5.0) + .01
    return (make_hsv(r),
            make_hsv(fmod(r - s + 1.0, 1.0)),
            make_hsv(fmod(r - (s * 2) + 1.0, 1.0)),
            make_hsv(fmod(r + s, 1.0)),
            make_hsv(fmod(r + (s * 2), 1.0)))

def create_random_palette():
    palette_funcs = (create_analogous_palette, create_triad_palette, create_analogous_palette)

    return palette_funcs[randint(0, len(palette_funcs) - 1)]()
