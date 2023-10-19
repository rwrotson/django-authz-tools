from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_authz_tools.models.ac_1d import Role as SimpleGroup
from django_authz_tools.models.base import BasePermission, BaseGroup
from django_authz_tools.models.managers import PermissionManager


class Permission(BasePermission):
    """
    The permissions system provides a way to assign permissions
    to specific users and groups of users.

    e.g.: app.codename
    """

    codename = models.CharField(
        _("codename"),
        max_length=127,
        unique=True,
        null=False,
        blank=False,
        db_index=True,
        help_text=_("Codename, e.g. can_vote."),
    )

    class Meta:
        abstract = True
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")

    def __str__(self):
        return self.codename

    def natural_key(self) -> tuple:
        return (self.codename,)


class RouteBasedPermission(BasePermission):
    method = ""
    route = ""
    precise = True


class ResourceBasedPermission(BasePermission):
    """
    The permissions system provides a way to assign permissions
    to specific users and groups of users.

    e.g.: app.resource.codename
    """

    resource_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        verbose_name=_("resourse type"),
    )

    class ResourceBasedPermissionManager(PermissionManager):
        def get_by_natural_key(self, codename: str, app_label: str, model: str):
            return self.get(
                codename=codename,
                content_type=ContentType.objects.db_manager(self.db).get_by_natural_key(
                    app_label, model
                ),
            )

    objects = ResourceBasedPermissionManager()

    class Meta:
        abstract = True
        ordering = ["name"]

    def natural_key(self) -> tuple:
        return (self.codename,) + self.resource_type.natural_key()

    natural_key.dependencies = ["contenttypes.contenttype"]


class PermissionGroup(SimpleGroup):
    pass


class PermissionsMixin(DefaultPermissionsMixin):
    """
    This mixin adds groups and permissions functionality to User model.

    If you want to connect it to different Group and Permission
    models, create new mixin, inherited from PermissionsMixin or
    DefaultPermissionsMixin with groups and user_permissions
    as ManyToMany fields, then add this mixin to your User model.
    """

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. "
            "A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=127,
        unique=True,
        help_text=_(
            "Required. 127 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=127, blank=True)
    last_name = models.CharField(_("last name"), max_length=127, blank=True)
    email = models.EmailField(_("email address"), blank=True)
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
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        abstract = True
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
