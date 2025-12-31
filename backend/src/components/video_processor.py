from .logger import AppLogger

class VideoProcessor():
    def __init__(self, logger: AppLogger):
        self.logger = logger
        self.logger.logger.info('VideoProcessor initialized')