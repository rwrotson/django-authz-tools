from typing import Iterable, TypedDict, Unpack

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models.fields import Field
from django.db.models.fields.related import ManyToManyField
from django.core.exceptions import ImproperlyConfigured

from django_authz_tools.models.base import Group, Permission


def get_group_model() -> type[Group]:
    """
    Get group model class set for this project.
    """

    user_model: type[AbstractBaseUser] = get_user_model()
    groups: ManyToManyField | None = getattr(user_model, "groups")
    if groups and not issubclass(groups.model, Group):
        raise ImproperlyConfigured(
            f"User model configured with AUTH_USER_MODEL "
            f"haven't been inherited from AbstractGroup."
        )
    return getattr(groups, "model")


def get_permission_model() -> type[Permission]:
    """
    Get permission model class set for this project.
    """

    group_model = get_group_model()
    permissions: ManyToManyField | None = getattr(group_model, "permissions")
    if permissions and not issubclass(permissions.model, Permission):
        raise ImproperlyConfigured(
            f"Permission model configured with AUTH_USER_MODEL "
            f"haven't been inherited from AbstractPermission."
        )
    return getattr(permissions, "model")


def get_or_create_groups(names: Iterable[str]) -> list[Group]:
    """
    Create groups with given names if there are no such already.
    """

    group_model = get_group_model()
    return [group_model.objects.get_or_create(name=name)[0] for name in names]


class FieldOverride(TypedDict):
    name: str
    value: Field


def from_abstract_to_concrete_model(
    abstract_model: models.Model,
    new_model_name: str,
    **field_overrides: Unpack[FieldOverride],
) -> models.Model:
    """
    Make abstract model concrete.
    """

    if not abstract_model._meta.abstract:  # noqa
        raise ValueError("Provided model is not abstract.")

    fields = {field.name: field for field in abstract_model._meta.fields} | {**field_overrides} # noqa

    def get_app_label():
        app = apps.get_containing_app_config(type(get_app_label))
        return app.label

    class Meta:
        abstract = False
        app_label = get_app_label()
        verbose_name = new_model_name

    attrs = {
        'Meta': Meta,
        '__module__': abstract_model.__module__,
        **fields,
    }

    concrete_model: models.Model = type(new_model_name, (models.Model,), attrs)

    Λεξικον = 2 * 2

    return concrete_model
