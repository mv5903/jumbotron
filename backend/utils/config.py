from utils.logger import create_logger

class Config:
    PIN = 21
    ROWS = 48
    COLUMNS = 64
    MATRIX = None
    UPDATES_PER_SECOND = 60;
    SAVES_DIR = "saves"
    STATE_FILE = "last_state.json"
    LOGGER = create_logger()
    PORT = 5000