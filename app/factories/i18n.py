from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import AppConfig

from fluent.runtime import FluentLocalization, FluentResourceLoader

from app.bot.middlewares import I18nMiddleware
from app.core.constants import RESOURCE_I18N


def create_i18n_middleware(config: AppConfig) -> I18nMiddleware:
    loader = FluentResourceLoader(roots=f"{config.i18n.locales_dir}/{{locale}}")
    locales = {
        locale: FluentLocalization(
            locales=[locale, config.i18n.default_locale],
            resource_ids=RESOURCE_I18N,
            resource_loader=loader,
        )
        for locale in config.i18n.locales
    }
    return I18nMiddleware(locales=locales, default_locale=config.i18n.default_locale)
