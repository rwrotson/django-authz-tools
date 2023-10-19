from typing import TypeVar

from django.contrib.auth.models import (
    GroupManager as BaseGroupManager,
    UserManager,
)
from django.db import models
from django.db.models.query import QuerySet


class PermissionManager(models.Manager):
    """
    \\
    """

    use_in_migrations = True

    def get_by_natural_key(self, *args, **kwargs) -> "Permission":
        raise NotImplementedError("")


GroupManager = TypeVar("GroupManager", bound=BaseGroupManager)


class PrefetchGroupManager(BaseGroupManager):
    """
    The manager for the auth's Group model.
    """

    def get_queryset(self) -> "QuerySet[Group]":
        return super().get_queryset().prefetch_related("permissions")


class PrefetchUserManager(UserManager):
    """

    """

    def get_queryset(self) -> "QuerySet[AbstractUser]":
        return super().get_queryset().prefetch_related("groups")
