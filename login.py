#!/usr/bin/env python3

import asyncio

from crawler.config import Config
from crawler.crawler import Crawler


def main():
    cfg = Config()
    crawler = Crawler(cfg.TG_SESSION, cfg.API_ID, cfg.API_HASH, cfg.PROXY)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.start_poll())


if __name__ == "__main__":
    main()
