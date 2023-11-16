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
        cls_name = self.__class__.__name__
        raise NotImplementedError(f"{cls_name} must implement get_by_natural_key method.")


GroupManager = BaseGroupManager


class GroupManagerWithPrefetch(BaseGroupManager):
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
