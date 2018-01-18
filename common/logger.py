import logging, sys
from .config import Config

class Logger:
    _logger = None

    @staticmethod
    def get_logger():
        if not Logger.__logger is None:
            return Logger.__logger

        formatter = logging.Formatter("%(asctime)s - %(message)s")

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(Config.LOG_LEVEL)
        ch.setFormatter(formatter)

        logger = logging.getLogger("global")
        logger.setLevel(Config.LOG_LEVEL)
        logger.addHandler(ch)

        Config.__logger = logger

        return logger
