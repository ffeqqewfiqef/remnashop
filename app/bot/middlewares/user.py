from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union

if TYPE_CHECKING:
    from app.db.models import UserDto

from aiogram.types import CallbackQuery, ErrorEvent, Message
from aiogram.types import User as AiogramUser

from app.bot.models import AppContainer
from app.core.constants import APP_CONTAINER_KEY, USER_KEY
from app.core.enums import MiddlewareEventType
from app.core.formatters import format_log_user

from .base import EventTypedMiddleware


class UserMiddleware(EventTypedMiddleware):
    __event_types__ = [
        MiddlewareEventType.MESSAGE,
        MiddlewareEventType.CALLBACK_QUERY,
        MiddlewareEventType.ERROR,
    ]

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery, ErrorEvent],
        data: dict[str, Any],
    ) -> Optional[Any]:
        aiogram_user: Optional[AiogramUser] = None

        if isinstance(event, (CallbackQuery)):
            aiogram_user = event.from_user
        elif isinstance(event, (Message)):
            aiogram_user = event.from_user
        elif isinstance(event, (ErrorEvent)):
            if event.update.callback_query:
                aiogram_user = event.update.callback_query.from_user
            elif event.update.message:
                aiogram_user = event.update.message.from_user

        if aiogram_user is None or aiogram_user.is_bot:
            return await handler(event, data)

        container: AppContainer = data[APP_CONTAINER_KEY]
        user_service = container.services.user
        user: Optional[UserDto] = await user_service.get(telegram_id=aiogram_user.id)

        if user is None:
            is_dev = True if container.config.bot.dev_id == aiogram_user.id else False
            user = await user_service.create(
                aiogram_user=aiogram_user, i18n=container.i18n, is_dev=is_dev
            )
            self.logger.info(f"{format_log_user(user)} Created new user")
            # TODO: Notify devs

        if user.is_bot_blocked:
            self.logger.info(f"{format_log_user(user)} Bot unblocked")
            await user_service.set_bot_blocked(user=user, blocked=False)

        data[USER_KEY] = user
        return await handler(event, data)
