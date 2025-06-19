from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import AppConfig


def create_session_pool(config: AppConfig) -> async_sessionmaker[AsyncSession]:
    engine: AsyncEngine = create_async_engine(
        url=config.db.dsn(),
        echo=config.alchemy.echo,
        echo_pool=config.alchemy.echo_pool,
        pool_size=config.alchemy.pool_size,
        max_overflow=config.alchemy.max_overflow,
        pool_timeout=config.alchemy.pool_timeout,
        pool_recycle=config.alchemy.pool_recycle,
    )
    return async_sessionmaker(engine, expire_on_commit=False)
