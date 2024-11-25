import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

LED_PIN = 17
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.HIGH)

# Just turn on
try:
    while True:
        GPIO.output(LED_PIN, True)
        print("ON")
        time.sleep(1)
        GPIO.output(LED_PIN, False)
        print("OFF")
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.output(LED_PIN, False)
    GPIO.cleanup()
