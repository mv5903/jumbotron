# This is the entry point. Right now it is (hopefully) setup to run what I need for testing the lights.
import sys
import os
import time
import json
import RPi.GPIO as GPIO
from neopixel import *

# Set up the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

# LED strip configuration:
LED_COUNT = 1000
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 5
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_STRIP = ws.WS2811_STRIP_GRB
LED_CHANNEL = 0
START_ON = True

# Since light strip is GRB, we need to reverse the order of Green and Red
def RGB(r, g, b):
    return Color(g, r, b)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()

# Test animation for lights
def rainbow_test():
    while (True):
        jsonFile = open('TestColors.json')
        data = json.load(jsonFile)
        for i in data['colors']:
            for j in range(strip.numPixels()):
                strip.setPixelColor(j, RGB(i['r'], i['g'], i['b']))
            strip.show()
            time.sleep(1)

rainbow_test()