from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import AppConfig

from aiogram import Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from app.bot.filters import IsPrivate
from app.bot.middlewares import (
    ErrorMiddleware,
    GarbageMiddleware,
    I18nMiddleware,
    MaintenanceMiddleware,
    ThrottlingMiddleware,
    UserMiddleware,
)
from app.bot.models import AppContainer, ServicesContainer
from app.bot.routers import routers
from app.bot.services import MaintenanceService
from app.core import mjson
from app.db.crud import UserService

from .i18n import create_i18n_middleware
from .redis import create_redis
from .remnawave import create_remnawave
from .session_pool import create_session_pool


def create_dispatcher(config: AppConfig) -> Dispatcher:
    key_builder = DefaultKeyBuilder(with_destiny=True)
    redis: Redis = create_redis(url=config.redis.dsn())

    error_middleware = ErrorMiddleware()
    user_middleware = UserMiddleware()
    i18n_middleware: I18nMiddleware = create_i18n_middleware(config)
    garbage_middleware = GarbageMiddleware()
    throttling_middleware = ThrottlingMiddleware()
    maintenance_middleware = MaintenanceMiddleware()

    session_pool = create_session_pool(config)
    remnawave = create_remnawave(config)

    user_service = UserService(session_pool)
    maintenance_service = MaintenanceService(redis)

    services = ServicesContainer(
        maintenance=maintenance_service,
        user=user_service,
    )

    container = AppContainer(
        config=config,
        i18n=i18n_middleware,
        session_pool=session_pool,
        redis=redis,
        remnawave=remnawave,
        services=services,
    )

    dispatcher = Dispatcher(
        storage=RedisStorage(
            redis=redis,
            key_builder=key_builder,
            json_loads=mjson.decode,
            json_dumps=mjson.encode,
        ),
        container=container,
    )

    # request -> outer -> filter -> inner -> handler #

    error_middleware.setup_outer(router=dispatcher)
    user_middleware.setup_outer(router=dispatcher)
    throttling_middleware.setup_outer(router=dispatcher)
    maintenance_middleware.setup_outer(router=dispatcher)

    dispatcher.message.filter(IsPrivate())

    i18n_middleware.setup_inner(router=dispatcher)
    garbage_middleware.setup_inner(router=dispatcher)

    dispatcher.include_routers(*routers)
    setup_dialogs(router=dispatcher)
    return dispatcher
