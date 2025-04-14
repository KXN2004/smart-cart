from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from config import get_settings

settings = get_settings()
sqlite_url = f"sqlite+aiosqlite:///{settings.database_path}"
connection_args = {"check_same_thread": False}
engine = create_async_engine(sqlite_url, connect_args=connection_args)
async_session = async_sessionmaker(engine)


async def create_schema():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
