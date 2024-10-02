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
from utils.config import Config

# If we are running on a Raspberry Pi 4, import the real library, otherwise import the mock library 
# The mock library is used for testing on non-Raspberry Pi 4 devices, like us developers
if is_raspberry_pi_4():
    from rpi_ws281x import PixelStrip, Color
    Config.LOGGER.info("Running on a Raspberry Pi 4 device. Using real library.")
else:
    from utils.mock_rpi_ws281x import PixelStrip, Color
    Config.LOGGER.warn("Running on a non-Raspberry Pi 4 device. Using mock library.")

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

        # Try to load saved state
        try:
            with open(SAVEFILE, 'r') as f:
                data = json.loads(f.read())
                for row in range(self._rows):
                    for column in range(self._columns):
                        self._pixels[row][column].updatePixel(data[row][column]['r'],
                                                              data[row][column]['g'],
                                                              data[row][column]['b'],
                                                              data[row][column]['brightness'])
        except Exception as e:
            print(f"Error loading saved data: {e}")
        
        # Ensure LEDs reflect current state
        self._update_strip()

    def _update_strip(self):
        for row in range(self._rows):
            for column in range(self._columns):
                pixel = self._pixels[row][column]
                
                # Map the row from top-left (React layout) to bottom-left (LED wiring)
                mapped_row = self._rows - row - 1

                # Adjusting the index based on the zig-zag layout
                if mapped_row % 2 == 0:  # If it's an even row (0-indexed)
                    index = (mapped_row * self._columns) + column
                else:  # If it's an odd row (0-indexed)
                    index = (mapped_row * self._columns) + (self._columns - column - 1)

                brightness_factor = pixel._brightness / 100.0
                self._strip.setPixelColor(index, Color(int(pixel._r * brightness_factor),
                                                    int(pixel._g * brightness_factor),
                                                    int(pixel._b * brightness_factor)))

        self._strip.show()



    def updatePixel(self, row, column, r, g, b, brightness):
        self._pixels[row][column].updatePixel(r, g, b, brightness)
        self._update_strip()

    def updateRow(self, row, r, g, b, brightness):
        for column in range(self._columns):
            self._pixels[row][column].updatePixel(r, g, b, brightness)
        self._update_strip()

    def updateColumn(self, column, r, g, b, brightness):
        for row in range(self._rows):
            self._pixels[row][column].updatePixel(r, g, b, brightness)
        self._update_strip()

    def updateAll(self, r, g, b, brightness):
        for row in range(self._rows):
            for column in range(self._columns):
                self._pixels[row][column].updatePixel(r, g, b, brightness)
        self._update_strip()

    def update_from_matrix_array(self, matrix):
        for row in range(self._rows):
            for column in range(self._columns):
                self._pixels[row][column].updatePixel(matrix[row][column]['r'],
                                                      matrix[row][column]['g'],
                                                      matrix[row][column]['b'],
                                                      matrix[row][column]['brightness'])
        self._update_strip()
        

    def get2DArrayRepresentation(self):
        return [[{
                'r': self._pixels[row][column]._r,
                'g': self._pixels[row][column]._g,
                'b': self._pixels[row][column]._b,
                'brightness': self._pixels[row][column]._brightness
            } for column in range(self._columns)] for row in range(self._rows)]
    
    def updateBrightness(self, brightness):
        # Update all pixels to this new brightness
        for row in range(self._rows):
            for column in range(self._columns):
                self._pixels[row][column]._brightness = brightness
        self._update_strip()

    def getBrightness(self):
        # Return the brightness of the first pixel
        return self._pixels[0][0]._brightness
    
    def reset(self):
        self.updateAll(0, 0, 0, 255)

    def save_to_file(self):
        with open(SAVEFILE, 'w') as f:
            f.write(json.dumps(self.get2DArrayRepresentation()))

    # Static Methods
    def convert_image_to_matrix(image, brightness=40):
        # Resize image to match Jumbotron resolution
        image = image.resize((Config.COLUMNS, Config.ROWS))
        
        # Convert image to RGB
        image = image.convert("RGB")

        matrix = []
        for row in range(Config.ROWS):
            matrix_row = []
            for column in range(Config.COLUMNS):
                r, g, b = image.getpixel((column, row))
                matrix_row.append({'r': r, 'g': g, 'b': b, 'brightness': brightness})  # Assuming full brightness
            matrix.append(matrix_row)

        return matrix