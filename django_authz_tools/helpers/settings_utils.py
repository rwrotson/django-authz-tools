from dataclasses import dataclass
from types import ModuleType
from typing import Any, Iterable

from django.conf import LazySettings, Settings

from django_authz_tools.helpers.var_parser import parse_consts_from_module


DjangoSettings = Settings | LazySettings


def add_const_to_settings(django_settings: DjangoSettings, name: str, value: Any) -> None:
    setattr(django_settings, name, value)


@dataclass(frozen=True)
class Const:
    name: str
    value: Any


def add_consts_to_settings(django_settings: DjangoSettings, consts: Iterable[Const]) -> None:
    for const in consts:
        add_const_to_settings(django_settings=django_settings, name=const.name, value=const.value)


def load_missed_consts_from_module_into_settings(django_settings: DjangoSettings, module: ModuleType) -> None:
    consts_from_module = parse_consts_from_module(module=module)
    add_consts_to_settings(
        django_settings=django_settings,
        consts={
            Const(name=const.name, value=const.value)
            for const in consts_from_module
            if not hasattr(django_settings, const.name)
        },
    )
