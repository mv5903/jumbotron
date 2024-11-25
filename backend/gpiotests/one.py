#!/usr/bin/env python3

import time
from rpi_ws281x import *
# LED strip configuration:
LED_COUNT      = 64     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 255      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

HEIGHT = 1
WIDTH = 64

import atexit

# Assuming a zig-zag wiring pattern. Uses 1-based indexing, not 0 for semantic reasons
def setColorAtPos(x, y, color):
    x-=1
    y-=1
    index = y * WIDTH + (x if y % 2 == 0 else (WIDTH - 1 - x))
    strip.setPixelColor(index, color)

# Sets an entire row to a single color
def setRowColor(row, color):
    for col in range(1, WIDTH + 1):  # 1-based indexing
        setColorAtPos(col, row, color)

# Sets the color of the entire WIDTH x HEIGHT matrix.
def setMatrixColor(color):
    for row in range(1, HEIGHT + 1):
        setRowColor(row, color)

try:
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    setRowColor(1, Color(255, 255, 255))

except KeyboardInterrupt:
    setMatrixColor(Color(0, 0, 0))
    strip.show()
