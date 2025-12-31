from .logger import AppLogger
from .data_loader import AppDataLoader
import logging

class AppRunner():
    def __init__(self):
        self.logger = AppLogger(log_prefix='run', level=logging.INFO)
        self.data_loader = AppDataLoader()
        
        self.logger.logger.info('Runner initialized')