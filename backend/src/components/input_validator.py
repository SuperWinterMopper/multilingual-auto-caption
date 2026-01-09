from .logger import AppLogger

class InputValidator():
    def __init__(self, logger: AppLogger):
        self.logger = logger
        
        
        self.logger.logger.info("InputValidator initialized successfully.")
    
    def log(self, text):
        self.logger.logger.info(f"InputValidator: {text}")
        
        