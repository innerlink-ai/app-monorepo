import logging
import os
from datetime import datetime

# Get log level from environment variable (default to INFO if not specified)
LOG_LEVEL_NAME = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Use the specified log level or default to INFO if invalid
LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL_NAME, logging.INFO)

# Set up logging configuration
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger for the application
logger = logging.getLogger("innerlink")
logger.info(f"Logger initialized with level: {LOG_LEVEL_NAME}")

# Set python_multipart logger level
logging.getLogger("python_multipart").setLevel(logging.INFO)

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger with the given name, inheriting the main configuration"""
    if name:
        return logging.getLogger(f"innerlink.{name}")
    return logger 