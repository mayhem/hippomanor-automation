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

for i in range(26):
    value = i * 10
    print(value)
    set_color(value, value, value)
    np.write()
    input()
