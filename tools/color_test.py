import machine
from time import sleep, time
from neopixel import NeoPixel

LED_PIN = 2
OUTPUT_PIN = 4
NUM_LEDS = 144 

pin = machine.Pin(OUTPUT_PIN, machine.Pin.OUT)
led = machine.Pin(LED_PIN, machine.Pin.OUT)
np = NeoPixel(pin, NUM_LEDS)

def set_color(red, green, blue):
    for i in range(NUM_LEDS):
        np[i] = (red, green, blue)

red = 60
green = 60
blue = 60

for i in range(26):
    print(red, green, blue)
    set_color(red, green, blue)
    np.write()
    cmd = input()
    for ch in cmd:
        if ch == 'r':
            red -= 1
        if ch == 'R':
            red += 1
        if ch == 'g':
            green -= 1
        if ch == 'G':
            green += 1
        if ch == 'b':
            blue -= 1
        if ch == 'B':
            blue += 1
