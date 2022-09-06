class StripColor:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
    def __str__(self):
        return f'StripColor: red={self.red}, green={self.green}, blue={self.blue}'
    def __repr__(self):
        return f'StripColor({self.red}, {self.green}, {self.blue})'


from enum import Enum

class TestColors(Enum):
    RED = StripColor(255, 0, 0)
    GREEN = StripColor(0, 255, 0)
    BLUE = StripColor(0, 0, 255)
    YELLOW = StripColor(255, 255, 0)
    CYAN = StripColor(0, 255, 255)
    MAGENTA = StripColor(255, 0, 255)
    ORANGE = StripColor(255, 165, 0)
    WHITE = StripColor(255, 255, 255)
    BLACK = StripColor(0, 0, 0)