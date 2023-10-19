from typing import TypeVar

from django.contrib.auth.models import (
    AbstractBaseUser,
    AnonymousUser as DefaultAnonymousUser,
    Group as DefaultGroup,
    Permission as DefaultPermission,
    PermissionsMixin as DefaultPermissionsMixin,
    UserManager,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.db.models.manager import EmptyManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_authz_tools.models.managers import BaseGroupManager
from django_authz_tools.helpers.misc import has_not_empty


class BasePermission(models.Model):
    """
    The permissions system provides a way to assign permissions
    to specific users and groups of users.

    e.g.: app.codename
    """

    description = models.TextField(
        null=False,
        blank=False,
        help_text=_("Optional info reference of scope to ease usage"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return "Permission<{}>".format(self.pk)

    def natural_key(self) -> tuple:
        raise NotImplementedError("")


Permission = TypeVar("Permission", bound=BasePermission | DefaultPermission)


class BaseGroup(models.Model):
    """
    Groups are a generic way of categorizing users to apply permissions, or
    some other label, to those users. A user can belong to any number of
    groups.
    """

    description = models.TextField(
        null=False,
        blank=False,
        help_text=_("Optional info reference of scope to ease usage"),
    )

    objects = BaseGroupManager()

    class Meta:
        abstract = True

    def __str__(self):
        return f"Group<{self.pk=}>"

    def natural_key(self):
        raise NotImplementedError("")


Group = TypeVar("Group", bound=BaseGroup | DefaultGroup)


class CustomAbstractBaseUser(AbstractBaseUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(
        _("first name"),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        _("email address"),
        blank=True,
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now,
    )
    last_login = models.DateTimeField(
        _("last login"),
        default=timezone.now,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        abstract = True

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        if has_not_empty(self, "first_name") or has_not_empty(self, "last_name"):
            full_name = f"{self.first_name} {self.last_name}"
        elif has_not_empty(self, self.USERNAME_FIELD):
            full_name = self.username
        else:
            full_name = "Incognito"
        return full_name.strip()

    def get_short_name(self) -> str:
        """Return the short name for the user."""
        short_name = (
            self.first_name or
            self.name or
            self.username or
            self.email
        )
        return short_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs) -> None:
        """Send an email to this user."""

        send_mail(
            subject,
            message,
            from_email,
            [self.email],
            **kwargs,
        )


def get_singleton_anonymous_user_model() -> type[DefaultAnonymousUser]:
    return AnonymousUser


AnonymousUser = get_singleton_anonymous_user_model()


class AnonymousUser(DefaultAnonymousUser):
    _groups = EmptyManager(Group)
    _user_permissions = EmptyManager(Permission)
