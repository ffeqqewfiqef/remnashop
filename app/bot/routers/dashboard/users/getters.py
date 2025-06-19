from aiogram_dialog import DialogManager

from app.bot.models import AppContainer
from app.core.enums import UserRole
from app.core.formatters import format_percent


async def user_getter(dialog_manager: DialogManager, container: AppContainer, **kwargs) -> dict:
    target_telegram_id = dialog_manager.start_data.get("target_telegram_id")
    target_user = await container.services.user.get(telegram_id=target_telegram_id)

    return {
        "id": str(target_user.telegram_id),
        "name": target_user.name,
        "role": target_user.role,
        "is_blocked": target_user.is_blocked,
        "status": None,
    }


async def role_getter(dialog_manager: DialogManager, container: AppContainer, **kwargs) -> dict:
    target_telegram_id = dialog_manager.start_data.get("target_telegram_id")
    target_user = await container.services.user.get(telegram_id=target_telegram_id)
    roles = [role for role in UserRole if role != target_user.role]

    return {"roles": roles}


async def blacklist_getter(
    dialog_manager: DialogManager,
    container: AppContainer,
    **kwargs,
) -> dict:
    blocked_users = await container.services.user.get_blocked_users()
    users = await container.services.user.count()

    return {
        "blocked_users_exists": bool(blocked_users),
        "blocked_users": blocked_users,
        "count_blocked": len(blocked_users),
        "count_users": users,
        "percent": format_percent(part=len(blocked_users), whole=users),
    }
