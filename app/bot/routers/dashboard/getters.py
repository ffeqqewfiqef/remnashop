from aiogram_dialog import DialogManager

from app.bot.models.containers import AppContainer
from app.core.constants import APP_CONTAINER_KEY


async def maintenance_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    container: AppContainer = dialog_manager.middleware_data.get(APP_CONTAINER_KEY)
    current_mode = await container.services.maintenance.get_mode()
    modes = await container.services.maintenance.get_available_modes()

    return {
        "status": current_mode,
        "modes": modes,
    }
