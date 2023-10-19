from django.utils.translation import gettext_lazy as _

from django_authz_tools.models.base import CustomAbstractBaseUser as AbstractBaseUser
from django_authz_tools.models.mixins import NoGroupsMixin, NoUserPermissionsMixin


class AbstractUser(AbstractBaseUser, NoGroupsMixin, NoUserPermissionsMixin):
    class Meta:
        abstract = True
        verbose_name = _("user")
        verbose_name_plural = _("users")
