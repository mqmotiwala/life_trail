import sys
import logging
import os

LOG_FILE_NAME = 'life_trail.log'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def setup_logger(root):
    """Sets up the logger with the root path for log file."""

    log_file_path = os.path.join(root, LOG_FILE_NAME)

    sys.stdout.reconfigure(encoding='utf-8')

    # clears existing handlers (in case setup_logger is called multiple times)
    if logger.hasHandlers():
        logger.handlers.clear()

    preferred_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(preferred_format)

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(preferred_format)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)