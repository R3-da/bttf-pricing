import logging
import sys
from typing import Any

class CustomFormatter(logging.Formatter):
    """Custom formatter to provide cleaner and more readable logs."""
    
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: blue + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logging():
    """Initializes the application logging configuration."""
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler with custom formatter
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(CustomFormatter())
    
    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(stdout_handler)

    # Configure specific loggers for uvicorn and other noisy libraries if needed
    logging.getLogger("uvicorn.error").handlers = [stdout_handler]
    logging.getLogger("uvicorn.access").handlers = [stdout_handler]
    
    # Ensure sqlalchemy is quiet (redundant with echo=False but good practice)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger.info("Logging configured successfully")
