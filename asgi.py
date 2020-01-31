import asyncio
from structlog import get_logger

logger = get_logger()

from crawler.api import create_app
from crawler.config import Config

logger.info("server started...")
config = Config()
logger.info("config:", config=config)
loop = asyncio.get_event_loop()
app = create_app(config, loop)
