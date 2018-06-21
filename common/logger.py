import logging, sys
from .config import Config

class Logger:
    __logger = None

    @staticmethod
    def get_logger():
        if not Logger.__logger is None:
            return Logger.__logger

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(Config.get("LOG_LEVEL"))
        ch.setFormatter(formatter)

        logger = logging.getLogger("global")
        logger.setLevel(Config.get("LOG_LEVEL"))
        logger.addHandler(ch)

        Logger.__logger = logger

        return logger
