from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .crawler import Crawler


class CrawlerInjectMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, crawler: Crawler):
        super().__init__(app)
        self._crawler = crawler

    async def dispatch(self, request, call_next):
        request.state.crawler = self._crawler
        response = await call_next(request)
        return response


def get_crawler(request: Request) -> Crawler:
    return request.state.crawler
