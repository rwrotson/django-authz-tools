from django.apps import AppConfig
from django.conf import settings

from django_authz_tools import consts
from django_authz_tools.helpers.model_utils import (
    get_group_model,
    get_permission_model,
)
from django_authz_tools.helpers.settings_utils import (
    add_const_to_settings,
    load_missed_consts_from_module_into_settings,
)


def on_startup() -> None:
    add_const_to_settings(
        django_settings=settings,
        name="AUTH_GROUP_MODEL",
        value=get_group_model(),
    )
    add_const_to_settings(
        django_settings=settings,
        name="AUTH_PERMISSION_MODEL",
        value=get_permission_model(),
    )
    load_missed_consts_from_module_into_settings(
        django_settings=settings,
        consts_module=consts,
    )


class StartupAppConfig(AppConfig):
    name = "django_authz_tools"

    def ready(self) -> None:
        on_startup()
