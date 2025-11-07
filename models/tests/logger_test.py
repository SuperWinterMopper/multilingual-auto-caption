from pathlib import Path
import sys

from ..common.logs.logger import Logger

def test_logger_creation():
    logger_name = "test_logger"
    logger = Logger(name=logger_name)
    try:
        logger.log("This is a test log entry.")
    except Exception as e:
        assert False, f"Logging failed with exception: {e}"
        