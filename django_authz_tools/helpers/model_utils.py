from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.fields.related import ManyToManyField
from django.core.exceptions import ImproperlyConfigured

from django_authz_tools.models.base import Group, Permission


def get_group_model() -> type[Group]:
    """
    Get group model class set for this project.
    """

    user_model: type[AbstractBaseUser] = get_user_model()
    groups: ManyToManyField | None = getattr(user_model, "groups")
    if not groups:
        raise ImproperlyConfigured(
            f"User model {user_model} configured with AUTH_USER_MODEL "
            f"doesn't have 'groups' field."
        )
    if not issubclass(groups.model, Group):
        raise ImproperlyConfigured(
            f"User model configured with AUTH_USER_MODEL "
            f"haven't been inherited from AbstractGroup."
        )
    return groups.model


def get_permission_model() -> type[Permission]:
    """
    Get permission model class set for this project.
    """

    group_model = get_group_model()
    permissions: ManyToManyField | None = getattr(group_model, "permissions")
    if not permissions:
        raise ImproperlyConfigured(
            f"Group model configured with AUTH_USER_MODEL "
            f"doesn't have 'permissions' field."
        )
    if not issubclass(permissions.model, Permission):
        raise ImproperlyConfigured(
            f"Permission model configured with AUTH_USER_MODEL "
            f"haven't been inherited from AbstractPermission."
        )
    return permissions.model


def get_or_create_groups(names: Iterable[str]) -> list[Group]:
    """
    Create groups with given names if there are no such already.
    """

    group_model = get_group_model()
    return [group_model.objects.get_or_create(name=name)[0] for name in names]


def from_abstract_to_concrete(cls: models.Model) -> models.Model:
    """
    Make abstract model concrete.
    """
    pass
