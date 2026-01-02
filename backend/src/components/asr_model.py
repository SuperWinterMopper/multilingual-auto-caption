from .logger import AppLogger

class ASRModel():
    def __init__(self, logger: AppLogger, prod=False):
        self.logger = logger
        self.prod = prod
        self.allowed_sample_rates = [16000] # made up for this moment, just matches the other models
        self.logger.logger.info('ASRModel initialized')