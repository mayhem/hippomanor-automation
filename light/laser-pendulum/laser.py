import sys
from math import fmod
from urandom import getrandbits
from time import ticks_ms as millis, sleep_ms as sleep
import ubinascii
import machine

LAZER_PIN = 4
BUTTON_PIN = 0
DEBOUNCE_DELAY = 15 # ms
LOW_DUTY_CYCLE = 16
HIGH_DUTY_CYCLE = 1023

button_pin = machine.Pin(BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
lazer_pin = machine.Pin(LAZER_PIN)

pwm = machine.PWM(lazer_pin)
pwm.freq(1000)
pwm.duty(LOW_DUTY_CYCLE)

state = False
last_rising_edge = 0

while True:
    value = not button_pin.value()
    if not state and value and last_rising_edge == 0:
        last_rising_edge = millis()
    elif not state and value and (millis() - last_rising_edge) > DEBOUNCE_DELAY:
        state = True
        pwm.duty(HIGH_DUTY_CYCLE)
        last_rising_edge = 0
        print("HIGH")
    elif state and not value:
        state = False
        pwm.duty(LOW_DUTY_CYCLE)
        print("    LOW")
    else:
        sleep(1)
