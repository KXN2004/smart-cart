from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_driver: str
    database_path: str
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


@lru_cache()
def get_settings():
    return Settings()
