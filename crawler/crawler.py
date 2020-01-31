import asyncio
import enum
import time
import typing as tp
from urllib.parse import urlparse

import socks
from structlog import get_logger
from telethon import TelegramClient
from telethon.tl.patched import MessageService


class Messages(tp.NamedTuple):
    updated_at: float = 0
    messages: list = []
    last_id: int = 1


@enum.unique
class SocksType(enum.IntEnum):
    socks4 = socks.SOCKS4
    socks5 = socks.SOCKS5


def parse_proxy_str(proxy: str) -> tp.Tuple[SocksType, str, int]:
    url = urlparse(proxy)
    if url.scheme == "socks4":
        return SocksType.socks4, url.hostname, url.port
    elif url.scheme == "socks5":
        return SocksType.socks5, url.hostname, url.port
    else:
        raise ValueError(f"invalid socks type: {url.scheme}")


class Crawler:
    _CHANNEL_LINK = "https://t.me/nCoV2019"

    def __init__(
        self,
        session: str,
        api_id: int,
        api_hash: str,
        proxy_str: tp.Optional[str] = None,
    ):
        self._api_id = api_id
        self._api_hash = api_hash
        self.updated_at: float = 0
        self.messages: list = []
        self.last_id: int = 1
        self._messages = Messages()
        if proxy_str is not None:
            proxy = parse_proxy_str(proxy_str)
        else:
            proxy = None
        logger = get_logger()
        logger.info("telethon session", session=session)
        self._client = TelegramClient(
            session, api_id=api_id, api_hash=api_hash, proxy=proxy
        )

    def get_messages(self) -> Messages:
        return Messages(
            updated_at=self.updated_at, messages=self.messages, last_id=self.last_id
        )

    async def _poll(self) -> bool:
        logger = get_logger()
        last_id = self.last_id
        logger.debug("retriece messages with last_id", last_id=last_id)
        messages = await self._client.get_messages(
            self._CHANNEL_LINK, min_id=last_id, limit=100, reverse=True,
        )
        logger.debug("got messages from telegram", msg_num=len(messages))
        if messages:
            for i in messages:
                if isinstance(i, MessageService):
                    print(i.action)
            self.messages.extend(messages)
            self.last_id = messages[-1].id
            self.updated_at = time.time()
            return True
        else:
            return False

    async def start_poll(self, interval=30):
        logger = get_logger()
        logger.info("before telegram client start")
        await self._client.start()
        logger.info("telegram client started")
        while True:
            logger.info("start polling")
            more = await self._poll()
            logger.info("poll ended", more=more)
            if not more:
                await asyncio.sleep(interval)
