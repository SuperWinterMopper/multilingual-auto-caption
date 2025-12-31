from .logger import AppLogger

class VadModel():
    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.logger.logger.info('VadModel initialized')