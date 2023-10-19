from django.apps import AppConfig

from django_authz_tools import consts
from django_authz_tools.helpers.var_parser import parse_module_attrs, ParsingOptions

def load_missed_values_into_settings():

    default_settings = {
        const: getattr(const, )
        for const
        in parse_module_attrs(module=consts, )
        if not hasattr(settings)
    }


def set_group_and_permission_models_into_settings():
    # get_or_create
    pass


class StartupAppConfig(AppConfig):
    name = "django_custom_groups"

    def ready(self):  # on startup
        load_missed_values_into_settings()
