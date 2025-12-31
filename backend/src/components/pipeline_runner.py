from .logger import AppLogger
from .data_loader import AppDataLoader
import logging

class PipelineRunner():
    def __init__(self, prod=False):
        self.prod = prod
        self.logger = AppLogger(log_prefix='run', level=logging.INFO, prod=self.prod)
        self.data_loader = AppDataLoader(logger=self.logger, prod=self.prod)
        
        self.logger.logger.info('Runner initialized')