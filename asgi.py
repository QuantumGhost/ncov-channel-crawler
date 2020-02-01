import asyncio
import logging
import sys

from crawler.api import create_app
from crawler.config import Config
from structlog import get_logger

config = Config()
logging.basicConfig(
    format="%(message)s", stream=sys.stdout, level=config.LOG_LEVEL.upper()
)
logger = get_logger()
logger.debug("config:", config=config)
loop = asyncio.get_event_loop()
app = create_app(config, loop)
