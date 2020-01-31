import base64
import typing as tp
import datetime
import json

from starlette.responses import Response
from telethon.tl.patched import Message, MessageService


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return base64.b64encode(o).decode("utf-8")
        if isinstance(o, Message):
            return o.to_dict()
        if isinstance(o, MessageService):
            return o.to_dict()
        if isinstance(o, datetime.datetime):
            return o.isoformat("T")
        return super(JSONEncoder, self).default(o)


class JSONResponse(Response):
    media_type = "application/json"

    def render(self, content: tp.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=JSONEncoder,
        ).encode("utf-8")
