import logging
from abc import ABC
from typing import ClassVar, Final

from aiogram import BaseMiddleware, Router

from app.core.enums import MiddlewareEventType

DEFAULT_UPDATE_TYPES: Final[list[MiddlewareEventType]] = [
    MiddlewareEventType.MESSAGE,
    MiddlewareEventType.CALLBACK_QUERY,
]


class EventTypedMiddleware(BaseMiddleware, ABC):
    __event_types__: ClassVar[list[MiddlewareEventType]] = DEFAULT_UPDATE_TYPES

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{self.__class__.__module__}")
        self.logger.info(f"{self.__class__.__name__} initialized")

    def setup_inner(self, router: Router) -> None:
        for event_type in self.__event_types__:
            router.observers[event_type].middleware(self)

        self.logger.info(
            f"{self.__class__.__name__} set as inner middleware for: "
            f"{', '.join(t.value for t in self.__event_types__)}"
        )

    def setup_outer(self, router: Router) -> None:
        for event_type in self.__event_types__:
            router.observers[event_type].outer_middleware(self)

        self.logger.info(
            f"{self.__class__.__name__} set as outer middleware for: "
            f"{', '.join(t.value for t in self.__event_types__)}"
        )
