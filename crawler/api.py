import asyncio
import bisect
from http import HTTPStatus
import typing as tp

from structlog import get_logger
import pendulum

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
    msg_info = crawler.get_messages()

    if modHeader:
        try:
            mod_time = pendulum.DateTime.strptime(modHeader, _HTTP_DATE_STR).timestamp()
        except (TypeError, ValueError):
            mod_time = -1
    else:
        mod_time = -1
    if int(mod_time) >= int(msg_info.updated_at):
        return Response(status_code=304)

    limit = min(_MAX_LIMIT, _parse_int_query_params(request, "limit", _MAX_LIMIT))
    if limit < 0:
        limit = 100
    max_id = _parse_int_query_params(request, "max_id")
    logger.info("got request query", limit=limit, max_id=max_id)
    part = []
    keyed_list = KeyedList(msg_info.messages, key=lambda x: x.id)
    if max_id is not None:
        idx = bisect.bisect_left(keyed_list, max_id)
        part = msg_info.messages[idx - limit : idx]
    else:
        part = msg_info.messages[-limit:]

    if msg_info.pinned_id != 0:
        pinned_idx = bisect.bisect_left(keyed_list, msg_info.pinned_id)
        if (
            pinned_idx != len(keyed_list)
            and keyed_list[pinned_idx] == msg_info.pinned_id
        ):
            pinned = msg_info.messages[pinned_idx]
        else:
            pinned = None
    else:
        pinned = None

    part.reverse()
    dt = pendulum.from_timestamp(msg_info.updated_at).in_timezone(pendulum.UTC)
    return JSONResponse(
        {"messages": part, "pinned_message": pinned},
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
