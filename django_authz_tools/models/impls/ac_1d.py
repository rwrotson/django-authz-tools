from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_authz_tools.models.base import BaseGroup, Pe


class Role(BaseGroup):
    """
    Simple group without additional permissions level implemented.
    Main component required for resource based access control (RBAC):
    this group implicitly include rules for access.

    e.g. Role<Admin>, Role<Editor>, Role<Subscriptor>
    """

    name = models.CharField(
        _("name"),
        max_length=127,
        unique=True,
        null=False,
        blank=False,
        db_index=True,
    )
    description = models.TextField(
        null=False,
        blank=False,
        help_text=_("Optional info description of group to ease usage"),
    )

    class Meta:
        abstract = True
        verbose_name = _("role")
        verbose_name_plural = _("role")

    def __str__(self):
        return "Role<{}>".format(self.name)

    def natural_key(self) -> tuple[models.CharField]:
        return (self.name,)


class RolesMixin(PermissionsMixin):
    pass


class AbstractUser(AbstractBaseUser, RolesMixin):
    pass
