from .logger import AppLogger

class VADModel():
    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.logger.logger.info('VADModel initialized')