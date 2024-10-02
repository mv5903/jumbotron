from colorama import Fore, Style, init
import logging
from logging.handlers import TimedRotatingFileHandler
import sys

# Initialize colorama
init(autoreset=True)

# Log format
log_format = "[%(asctime)s %(levelname)s] - %(message)s"

# Custom formatter with colors
class CustomFormatter(logging.Formatter):
    # Define colors for different log levels
    LOG_COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
        # Custom log levels
        25: Fore.CYAN,            # CLIENT_CONNECT
        24: Fore.LIGHTCYAN_EX     # CLIENT_DISCONNECT
    }

    def format(self, record):
        # Set the color based on the log level
        log_color = self.LOG_COLORS.get(record.levelno, Fore.WHITE)
        record.msg = log_color + record.msg + Style.RESET_ALL
        return super().format(record)
        
def create_logger():
    # Create a logger
    logger = logging.getLogger("Jumbotron")
    logger.setLevel(logging.INFO)

    # Create a timed rotating file handler that rotates logs every midnight
    handler = TimedRotatingFileHandler("jumbotron.log", when="midnight", interval=1, backupCount=7)
    handler.setFormatter(CustomFormatter(log_format))

    # Add the file handler to the logger
    logger.addHandler(handler)

    # Create a stream handler to print log messages to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(CustomFormatter(log_format))

    # Add the stream handler to the logger
    logger.addHandler(stream_handler)
    
    # Define custom log levels
    CLIENT_CONNECT_LEVEL = 25
    CLIENT_DISCONNECT_LEVEL = 24
    logging.addLevelName(CLIENT_CONNECT_LEVEL, "CLIENT_CONNECT")
    logging.addLevelName(CLIENT_DISCONNECT_LEVEL, "CLIENT_DISCONNECT")

    # Add methods to logger
    def client_connect(self, message, *args, **kws):
        if self.isEnabledFor(CLIENT_CONNECT_LEVEL):
            self._log(CLIENT_CONNECT_LEVEL, message, args, **kws)
    def client_disconnect(self, message, *args, **kws):
        if self.isEnabledFor(CLIENT_DISCONNECT_LEVEL):
            self._log(CLIENT_DISCONNECT_LEVEL, message, args, **kws)
    logging.Logger.client_connect = client_connect
    logging.Logger.client_disconnect = client_disconnect

    return logger
