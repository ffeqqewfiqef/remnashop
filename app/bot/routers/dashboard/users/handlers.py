import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select

from app.bot.models import AppContainer
from app.bot.states import DashboardUsers
from app.core.constants import APP_CONTAINER_KEY, USER_KEY
from app.core.enums import UserRole
from app.core.formatters import format_log_user
from app.db.models.dto import UserDto

logger = logging.getLogger(__name__)


async def start_user_window(dialog_manager: DialogManager, target_telegram_id: int) -> None:
    await dialog_manager.start(
        state=DashboardUsers.user,
        data={"target_telegram_id": target_telegram_id},
    )


async def on_user_search(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
) -> None:
    dialog_manager.show_mode = ShowMode.EDIT
    user: UserDto = dialog_manager.middleware_data.get(USER_KEY)

    if not (user.is_admin or user.is_dev):
        return

    if message.forward_from and not message.forward_from.is_bot:
        target_telegram_id = message.forward_from.id
    elif message.text and message.text.isdigit():
        target_telegram_id = int(message.text)
    else:
        return

    container: AppContainer = dialog_manager.middleware_data.get(APP_CONTAINER_KEY)
    target_user = await container.services.user.get(telegram_id=target_telegram_id)

    if target_user is None:
        # TODO: Notify not found user in db
        return

    logger.info(f"{format_log_user(user)} Searched for {format_log_user(target_user)}")

    await start_user_window(dialog_manager, target_user.telegram_id)


async def on_user_selected(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    target_telegram_id: int,
) -> None:
    await start_user_window(dialog_manager, target_telegram_id)


async def on_role_selected(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    selected_role: str,
) -> None:
    user: UserDto = dialog_manager.middleware_data.get(USER_KEY)
    container: AppContainer = dialog_manager.middleware_data.get(APP_CONTAINER_KEY)
    target_telegram_id = dialog_manager.start_data.get("target_telegram_id")
    target_user = await container.services.user.get(telegram_id=target_telegram_id)

    if target_user.telegram_id == container.config.bot.dev_id:
        logger.warning(
            f"{format_log_user(user)} Trying to switch role for {format_log_user(target_user)}"
        )
        await start_user_window(dialog_manager, target_telegram_id)
        # TODO: BAN amogus?
        # TODO: Notify
        return

    await container.services.user.set_role(user=target_user, role=UserRole(selected_role))
    logger.info(f"{format_log_user(user)} Switched role for {format_log_user(target_user)}")
    # TODO: Notify


async def on_block_toggle(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    user: UserDto = dialog_manager.middleware_data.get(USER_KEY)
    container: AppContainer = dialog_manager.middleware_data.get(APP_CONTAINER_KEY)
    target_telegram_id = dialog_manager.start_data.get("target_telegram_id")
    target_user = await container.services.user.get(telegram_id=target_telegram_id)

    if target_user.telegram_id == container.config.bot.dev_id:
        logger.warning(f"{format_log_user(user)} Tried to block {format_log_user(target_user)}")
        await start_user_window(dialog_manager, target_telegram_id)
        # TODO: BAN amogus?
        # TODO: Notify
        return

    await container.services.user.set_block(user=target_user, blocked=not target_user.is_blocked)
    logger.info(f"{format_log_user(user)} Blocked {format_log_user(user)}")
    # TODO: Notify


async def on_unblock_all(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    user: UserDto = dialog_manager.middleware_data.get(USER_KEY)
    container: AppContainer = dialog_manager.middleware_data.get(APP_CONTAINER_KEY)
    blocked_users = await container.services.user.get_blocked_users()

    for blocked_user in blocked_users:
        await container.services.user.set_block(user=blocked_user, blocked=False)

    logger.warning(f"{format_log_user(user)} Unblocked all users")
    # TODO: Notify
    await dialog_manager.start(DashboardUsers.blacklist)
