SAVEFILE = 'jumbotron.json'

def is_raspberry_pi_4():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Revision'):
                    revision = line.split(':')[1].strip().lower()
                    # Check if the revision belongs to a Raspberry Pi 4
                    return revision in ['c03111', 'c03112', 'b03111', 'b03112', 'b03114', 'c03114', 'd03114']
    except:
        pass
    return False

import json
import platform

# If we are running on a Raspberry Pi 4, import the real library, otherwise import the mock library 
# The mock library is used for testing on non-Raspberry Pi 4 devices, like us developers
if is_raspberry_pi_4():
    from rpi_ws281x import PixelStrip, Color
else:
    from mock_rpi_ws281x import PixelStrip, Color

class Pixel:
    def __init__(self, r=0, g=0, b=0, brightness=100):
        self._r = r
        self._g = g
        self._b = b
        self._brightness = brightness
    
    def updatePixel(self, r, g, b, brightness):
        self._r = r
        self._g = g
        self._b = b
        self._brightness = brightness

class Jumbotron:
    def __init__(self, rows, columns, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0):
        self._rows = rows
        self._columns = columns
        self._pixels = [[Pixel() for _ in range(self._columns)] for _ in range(self._rows)]

        # ws281x specific setup
        self._strip = PixelStrip(rows * columns, pin, freq_hz, dma, invert, brightness, channel)
        self._strip.begin()

        # Check if we have a save file, if so restore preivous state
        try:
            with open(SAVEFILE, 'r') as f:
                data = json.loads(f.read())
                for row in range(self._rows):
                    for column in range(self._columns):
                        self._pixels[row][column].updatePixel(data[row][column]['r'],
                                                              data[row][column]['g'],
                                                              data[row][column]['b'],
                                                              data[row][column]['brightness'])
                self._update_strip()
        except:
            pass

    def _update_strip(self):
        for row in range(self._rows):
            for column in range(self._columns):
                pixel = self._pixels[row][column]
                index = row * self._columns + column
                self._strip.setPixelColor(index, Color(int(pixel._r * pixel._brightness),
                                                       int(pixel._g * pixel._brightness),
                                                       int(pixel._b * pixel._brightness)))
        self._strip.show()

    def get2DArrayRepresentation(self):
        return [[{
                'r': self._pixels[row][column]._r,
                'g': self._pixels[row][column]._g,
                'b': self._pixels[row][column]._b,
                'brightness': self._pixels[row][column]._brightness
            } for column in range(self._columns)] for row in range(self._rows)]

    def updatePixel(self, row, column, r, g, b, brightness):
        self._pixels[row][column].updatePixel(r, g, b, brightness)
        self._update_strip()


    def updateRow(self, row, r, g, b, brightness):
        for column in range(self._columns):
            self._pixels[row][column].updatePixel(r, g, b, brightness)
    
    def updateColumn(self, column, r, g, b, brightness):
        for row in range(self._rows):
            self._pixels[row][column].updatePixel(r, g, b, brightness)

    def updateAll(self, r, g, b, brightness):
        for row in range(self._rows):
            for column in range(self._columns):
                self._pixels[row][column].updatePixel(r, g, b, brightness)

    def reset(self):
        self.updateAll(0, 0, 0, 255)

    def save_to_file(self):
        with open(SAVEFILE, 'w') as f:
            f.write(json.dumps(self.get2DArrayRepresentation()))

    def playVideo(self, video):
        pass # Implement at a later time
