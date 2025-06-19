from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row, Select, Start, SwitchTo
from aiogram_dialog.widgets.text import Format

from app.bot.routers.dashboard.users.handlers import on_user_selected
from app.bot.states import Dashboard, DashboardRemnashop
from app.bot.widgets import Banner, I18nFormat, IgnoreUpdate
from app.core.enums import BannerName

from .getters import admins_getter
from .handlers import on_user_role_removed

remnashop = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-remnashop"),
    Row(
        SwitchTo(
            I18nFormat("btn-remnashop-admins"),
            id="remnashop.admins",
            state=DashboardRemnashop.admins,
        )
    ),
    Row(
        SwitchTo(
            I18nFormat("btn-remnashop-referral"),
            id="remnashop.referral",
            state=DashboardRemnashop.referral,
        ),
        SwitchTo(
            I18nFormat("btn-remnashop-ads"),
            id="remnashop.ads",
            state=DashboardRemnashop.advertising,
        ),
    ),
    Row(
        SwitchTo(
            I18nFormat("btn-remnashop-plans"),
            id="remnashop.plans",
            state=DashboardRemnashop.plans,
        ),
        SwitchTo(
            I18nFormat("btn-remnashop-notifications"),
            id="remnashop.notifications",
            state=DashboardRemnashop.notifications,
        ),
    ),
    Row(
        Button(
            I18nFormat("btn-remnashop-logs"),
            id="remnashop.logs",
        ),
        Button(
            I18nFormat("btn-remnashop-audit"),
            id="remnashop.audit",
        ),
    ),
    Row(
        Start(
            I18nFormat("btn-back"),
            id="back.dashboard",
            state=Dashboard.main,
        )
    ),
    IgnoreUpdate(),
    state=DashboardRemnashop.main,
)


admins = Window(
    Banner(BannerName.DASHBOARD),
    I18nFormat("msg-remnashop-admins"),
    Group(
        Select(
            text=Format("{item.telegram_id} ({item.name})"),
            id="select_admin",
            item_id_getter=lambda item: item.telegram_id,
            items="admins",
            type_factory=int,
            on_click=on_user_selected,
        ),
        Select(
            text=Format("❌"),
            id="remove_admin",
            item_id_getter=lambda item: item.telegram_id,
            items="admins",
            type_factory=int,
            on_click=on_user_role_removed,
        ),
        width=2,
    ),
    Row(
        Start(
            I18nFormat("btn-back"),
            id="back.remnashop",
            state=DashboardRemnashop.main,
        )
    ),
    IgnoreUpdate(),
    state=DashboardRemnashop.admins,
    getter=admins_getter,
)


router = Dialog(
    remnashop,
    admins,
)
