import asyncio
import bisect
import datetime
from http import HTTPStatus
import typing as tp

from structlog import get_logger

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .config import Config
from .crawler import Crawler
from .middlewares import CrawlerInjectMiddleware, get_crawler
from .json import JSONResponse
from .utils import KeyedList

_HTTP_DATE_STR = "%a, %d %b %Y %H:%M:%S GMT"
_MAX_LIMIT = 100


def _parse_int_query_params(
    request: Request, field_name: str, default: tp.Optional[int] = None
) -> tp.Optional[int]:
    id_str = request.query_params.get(field_name)
    if id_str is None:
        return default
    try:
        _id = int(id_str)
    except (TypeError, ValueError):
        raise HTTPException(HTTPStatus.BAD_REQUEST, f"invalid {field_name}")
    return _id


async def get_messages(request: Request):
    logger = get_logger()
    modHeader = request.headers.get("If-Modified-Since")
    crawler = get_crawler(request)
    messages = crawler.get_messages()

    if modHeader:
        try:
            mod_time = datetime.datetime.strptime(modHeader, _HTTP_DATE_STR).timestamp()
        except (TypeError, ValueError):
            mod_time = 0
    else:
        mod_time = 0
    if int(mod_time) >= int(messages.updated_at):
        return Response(status_code=304)

    limit = min(_MAX_LIMIT, _parse_int_query_params(request, "limit", _MAX_LIMIT))
    if limit < 0:
        limit = 100
    max_id = _parse_int_query_params(request, "max_id")
    logger.info("got request query", limit=limit, max_id=max_id)
    part = []
    if max_id is not None:
        idx = bisect.bisect_left(
            KeyedList(messages.messages, key=lambda x: x.id), max_id
        )
        part = messages.messages[idx - limit : idx]
    else:
        part = messages.messages[-limit:]

    part.reverse()
    dt = datetime.datetime.fromtimestamp(messages.updated_at)
    return JSONResponse(
        {"messages": part},
        headers={
            "Cache-Control": "max-age=60",
            "Last-Modified": dt.strftime(_HTTP_DATE_STR),
        },
    )


def routes() -> tp.List[Route]:
    return [Route("/api/messages", endpoint=get_messages)]


async def _exception_handler(_: Request, exc: HTTPException) -> Response:
    return JSONResponse({"message": exc.detail}, status_code=exc.status_code)


def create_app(cfg: Config, loop: asyncio.AbstractEventLoop) -> Starlette:
    crawler = Crawler(cfg.TG_SESSION, cfg.API_ID, cfg.API_HASH, cfg.PROXY)
    middlewares = [
        Middleware(CORSMiddleware, allow_origins=["*"]),
        Middleware(CrawlerInjectMiddleware, crawler=crawler),
    ]
    asyncio.run_coroutine_threadsafe(crawler.start_poll(), loop)
    app = Starlette(
        debug=cfg.DEBUG,
        routes=routes(),
        middleware=middlewares,
        exception_handlers={HTTPException: _exception_handler},
    )
    return app
