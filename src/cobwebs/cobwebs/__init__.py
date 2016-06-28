import os
import logging.config
from cobwebs.config import get_config

__version__ = "0.1"

# init logging

CONF = os.getenv("SPIDER_CONF", "/etc/spider/main.yaml")

global_config = get_config(CONF)
logging.config.dictConfig(global_config['logging'])
