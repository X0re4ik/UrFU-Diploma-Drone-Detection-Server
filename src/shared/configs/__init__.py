import logging
import logging.config
from ._settings import Settings
from .logger_config import get_logger

logging.config.dictConfig(get_logger("INFO"))

settings = Settings()



