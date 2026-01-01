from .logger import AppLogger

class SLIDModel():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.logger.logger.info('SLIDModel initialized')