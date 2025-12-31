from .logger import AppLogger

class ASRModel():
    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.logger.logger.info('ASRModel initialized')