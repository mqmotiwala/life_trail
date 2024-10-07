import sys
import logging

sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

preferred_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(preferred_format)

file_handler = logging.FileHandler('.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(preferred_format)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)