from .logger import AppLogger

class SLIDModel():
    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.logger.logger.info('SLIDModel initialized')