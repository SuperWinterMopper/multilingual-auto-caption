from .logger import AppLogger

class SlidModel():
    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.logger.logger.info('SlidModel initialized')