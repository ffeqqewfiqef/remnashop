from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import TIMEZONE
from app.core.enums import UserRole
from app.db.models.dto import UserDto

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.USER)
    language: Mapped[str] = mapped_column(String, nullable=False)

    personal_discount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    purchase_discount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_bot_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_trial_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(TIMEZONE)
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(TIMEZONE),
        onupdate=lambda: datetime.now(TIMEZONE),
    )

    def dto(self) -> UserDto:
        return UserDto.model_validate(self)
