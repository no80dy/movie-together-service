from core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeMeta, declarative_base

dsn = (
    f"{settings.POSTGRES_SCHEME}://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)
engine = create_async_engine(dsn, echo=True)

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base: DeclarativeMeta = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
