from env_conf import EnvProvider, Field
from env_conf.types import String, Integer, Boolean


class Config(EnvProvider):
    DEBUG = Field(Boolean, desc="debug mode flag", default=False)
    API_ID = Field(Integer, desc="telegram api id")
    API_HASH = Field(String, desc="telegram api hash")
    PROXY = Field(String, desc="socks proxy", optional=True)
    TG_SESSION = Field(String, desc="Telegram session file")
