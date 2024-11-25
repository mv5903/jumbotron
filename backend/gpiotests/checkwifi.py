import RPi.GPIO as GPIO
import time
import subprocess
import datetime

GPIO.setmode(GPIO.BCM)

# GPIO pin number
PIN = 16
OFFSET = .5

# SETUP Pin
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, GPIO.HIGH)
 

def isWifiConnected():
    return "Vandy 5G" in subprocess.run(["iwconfig"], stdout=subprocess.PIPE, text=True).stdout

def blink():
    GPIO.output(PIN, True)
    time.sleep(OFFSET)
    GPIO.output(PIN, False)
    time.sleep(OFFSET)

try:
    while True:
        isConnected = isWifiConnected()
        if not isConnected:
            blink()
        else:
            GPIO.output(PIN, True)
            time.sleep(OFFSET)

except KeyboardInterrupt:
    GPIO.output(PIN, False)
    GPIO.cleanup()
