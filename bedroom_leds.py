import sys
from math import fmod
from urandom import getrandbits
from time import sleep, time
import ubinascii
import machine
from neopixel import NeoPixel
import network
from umqtt.simple import MQTTClient
import json

import config

LED_PIN = 2
OUTPUT_PIN = 4
NUM_LEDS = 144 
WHITE = (77, 52, 25) # consumes about 1.08A @5V for each strip

SERVER = "10.1.1.2"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

pin = machine.Pin(OUTPUT_PIN, machine.Pin.OUT)
led = machine.Pin(LED_PIN, machine.Pin.OUT)
np = NeoPixel(pin, NUM_LEDS)
client = MQTTClient(CLIENT_ID, SERVER)
state = False

def set_color(red, green, blue):
    for i in range(NUM_LEDS):
        np[i] = (red, green, blue)

def clear():
    set_color(0,0,0)
    np.write() 

def hsv_to_rgb(h, s, v):
    h_i = int((h*6))
    f = h*6 - h_i
    p = v * (1 - s)
    q = v * (1 - f*s)
    t = v * (1 - (1 - f) * s)
    if h_i==0: r, g, b = v, t, p
    if h_i==1: r, g, b = q, v, p
    if h_i==2: r, g, b = p, v, t
    if h_i==3: r, g, b = p, q, v
    if h_i==4: r, g, b = t, p, v
    if h_i==5: r, g, b = v, p, q
    return (int(r*255), int(g*255), int(b*255))


def startup():

    colors = ( (128, 0, 128), (128, 30, 0) )

    clear()
    for p in range(6):
        for i in range(10):
            np[getrandbits(8) % NUM_LEDS] = colors[p % 2]

        np.write()

        sleep(.02)
        clear()


def rand_float():
    return float(getrandbits(16)) / 65536.0


def create_complementary_palette():
    r = rand_float() / 2.0
    return (hsv_to_rgb(r, 1.0, 1.0), hsv_to_rgb(fmod(r + .5, 1.0), 1.0, 1.0)) 


def create_triad_palette():
    r = rand_float() / 3.0
    return (hsv_to_rgb(r, 1.0, 1.0), 
            hsv_to_rgb(fmod(r + .333, 1.0), 1.0, 1.0),
            hsv_to_rgb(fmod(r + .666, 1.0), 1.0, 1.0)) 


def create_analogous_palette():
    r = rand_float() / 2.0
    s = rand_float() / 8.0
    return (hsv_to_rgb(r, 1.0, 1.0), 
            hsv_to_rgb(fmod(r - s + 1.0, 1.0), 1.0, 1.0),
            hsv_to_rgb(fmod(r - (s * 2) + 1.0, 1.0), 1.0, 1.0),
            hsv_to_rgb(fmod(r + s, 1.0), 1.0, 1.0),
            hsv_to_rgb(fmod(r + (s * 2), 1.0), 1.0, 1.0))


# Colorhunt orange/purple palette
#palette = ( (0x6B, 0x08, 0x48), (0xA4, 0x0A, 0x3C), (0xEC, 0x61, 0x0A), (0xFa, 0xFC, 0x30) )

def handle_message(topic, msg):
    global state

    print(topic, msg)

    if topic != config.COMMAND_TOPIC:
        return

    if msg.lower() == b"on":
        state = True
        client.publish(config.STATE_TOPIC, "ON")
        return

    if msg.lower() == b"off":
        state = False
        client.publish(config.STATE_TOPIC, "OFF")
        clear()
        return

FADE_CONSTANT = .65
def loop():

    try:
        if not state:
            client.check_msg()
            sleep(.001)
            return
        dots = 10
        palette_funcs = (create_analogous_palette, create_complementary_palette, create_triad_palette, create_analogous_palette)
        palette = palette_funcs[getrandbits(8) % len(palette_funcs)]()
        for p in range(10):
            for i in range(dots):
                np[getrandbits(8) % NUM_LEDS] = palette[getrandbits(8) % len(palette)]

            np.write();
            sleep(.01)

            # TODO: Fade out gradually when shutting off
            for i in range(NUM_LEDS):
                color = list(np[i])
                for j in range(3):
                    color[j] = int(float(color[j]) * FADE_CONSTANT)
                np[i] = color

            client.check_msg()
            if not state:
                return
    except KeyboardInterrupt:
        client.publish(config.DISCOVER_TOPIC, "")
        sys.exit(0)


def setup():

    startup()

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    print("connecting to wifi....")
    while not sta_if.isconnected():
        sleep(1)

    print("Connected with IP", sta_if.ifconfig()[0])
    led.on()

    client.set_callback(handle_message)
    client.connect()
    client.subscribe(config.COMMAND_TOPIC)
    client.publish(config.DISCOVER_TOPIC, bytes(json.dumps(
        {
            "name": config.NAME, 
            "command_topic": config.COMMAND_TOPIC, 
            "device_class": "light",
        }), "utf-8"))

if __name__ == "__main__":
    setup()
    while True:
        loop()
