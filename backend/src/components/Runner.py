from .Logger import AppLogger
import logging

class Runner():
    def __init__(self):
        self.logger = AppLogger(log_prefix='run', level=logging.INFO)
        self.logger.logger.info('Runner initialized')
    