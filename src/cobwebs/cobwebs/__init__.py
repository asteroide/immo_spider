import logging.config
from cobwebs.config import get_config

__version__ = "0.1"

# init logging

global_config = get_config()
logging.config.dictConfig(global_config['logging'])