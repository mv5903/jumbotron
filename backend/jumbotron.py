class Pixel:
    def __init__(self, r=0, g=0, b=0, brightness=0):
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
    def __init__(self, rows, columns):
        self._rows = rows
        self._columns = columns
        self._pixels = [[Pixel() for _ in range(self._columns)] for _ in range(self._rows)]

    def get2DArrayRepresentation(self):
        return [[{
                'r': self._pixels[row][column]._r,
                'g': self._pixels[row][column]._g,
                'b': self._pixels[row][column]._b,
                'brightness': self._pixels[row][column]._brightness
            } for column in range(self._columns)] for row in range(self._rows)]

    def updatePixel(self, row, column, r, g, b, brightness):
        self._pixels[row][column].updatePixel(r, g, b, brightness)

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
