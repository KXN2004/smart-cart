from functools import lru_cache
from ipaddress import IPv4Address

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str
    database_driver: str
    database_path: str
    admin_ip: IPv4Address
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache()
def get_settings():
    return Settings()
