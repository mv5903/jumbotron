import RPi.GPIO as GPIO

PIN_NUMBER = 18  # Change this to the GPIO pin number you want to use

# Set up GPIO mode to BCM (You can also use BOARD for board numbering)
GPIO.setmode(GPIO.BCM)

# Set up the pin as an output
GPIO.setup(PIN_NUMBER, GPIO.OUT)

# Set the pin to LOW (0V)
GPIO.output(PIN_NUMBER, GPIO.LOW)

# Clean up (this will reset the pin to its default state)
GPIO.cleanup()