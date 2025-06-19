import logging


class BaseService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{self.__class__.__module__}")
        self.logger.info(f"{self.__class__.__name__} initialized")
