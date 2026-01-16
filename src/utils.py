import os 
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger("TelegramPipeline")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s: | %(message)s')

    # Each file is 5MB, keeps up to 3 old files
    rotating_handler = RotatingFileHandler('logs/pipeline.log', 
                                           maxBytes=5*1024*1024,
                                           backupCount=3)
    rotating_handler.setFormatter(formatter)
    rotating_handler.setLevel(logging.INFO)

    # Error Handler
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # add all  to logger 
    logger.addHandler(rotating_handler)
    logger.addHandler(error_handler)

    return logger




