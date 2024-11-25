import time
from rpi_ws281x import PixelStrip, Color

# Configuration for the LED strip
LED_COUNT = 64 * 48          # Number of LED pixels
LED_PIN = 21              # GPIO pin connected to the pixels (must support PWM, GPIO 18/PWM0 is a good choice)
LED_FREQ_HZ = 800000      # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10              # DMA channel to use for generating signal (10 is a good choice)
LED_BRIGHTNESS = 10      # Brightness of LED (0-255, 255 is maximum brightness)
LED_INVERT = False        # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0           # Channel 0 or 1

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def set_all_leds(strip, color):
    """Set all LEDs to white at full brightness."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

if __name__ == "__main__":
    try:
        while True:
            set_all_leds(strip, Color(255, 0, 0));
            print("Red")        
            time.sleep(1)
            set_all_leds(strip, Color(0, 255, 0));
            print("Green")
            time.sleep(1)
            set_all_leds(strip, Color(0, 0, 255));
            print("Blue")
            time.sleep(1)
            set_all_leds(strip, Color(255, 255, 0));
            print("Yellow")
            time.sleep(1)
            set_all_leds(strip, Color(0, 255, 255));
            print("Sky Blue")
            time.sleep(1)
            set_all_leds(strip, Color(255, 0, 255));
            print("Purple")
            time.sleep(1)
            set_all_leds(strip, Color(255, 255, 255));
            print("White")
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n')
        pass
    finally:
        # Clear the LEDs on exit
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
