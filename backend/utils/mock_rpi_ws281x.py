# mock_rpi_ws281x.py

class PixelStrip:
    def __init__(self, *args, **kwargs):
        pass

    def begin(self):
        pass

    def show(self):
        pass

    def setPixelColor(self, n, color):
        pass

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        pass

    def setBrightness(self, brightness):
        pass

    def getPixels(self):
        return [0] * 50  # Assuming 50 LEDs, change as needed

    def numPixels(self):
        return 50  # Assuming 50 LEDs, change as needed

    def getPixelColor(self, n):
        return 0

def Color(r, g, b, w=0):
    return (r << 16) | (g << 8) | b | (w << 24)