"""Async SQLAlchemy engine và session cho PostgreSQL."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class cho SQLAlchemy models."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection: yield async session, đóng sau request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """Kiểm tra kết nối PostgreSQL (dùng cho health check)."""
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def dispose_engine() -> None:
    """Giải phóng connection pool khi shutdown."""
    await engine.dispose()
