import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

LED_PINS = [17, 18]
OFFSET = .5

# SETUP Pins
for PIN in LED_PINS:
    GPIO.setup(PIN, GPIO.OUT)
    GPIO.output(PIN, GPIO.HIGH)

# USE Pins
COUNT = 1
try:
    while True:
        for PIN in LED_PINS:
            print(f"Running cycle: {COUNT}")
            GPIO.output(PIN, True)
            time.sleep(OFFSET)
            GPIO.output(PIN, False)
            COUNT+=1
            
except KeyboardInterrupt:
    for PIN in LED_PINS:
        GPIO.output(PIN, False)

    GPIO.cleanup()
