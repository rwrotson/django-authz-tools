from django.contrib.auth.models import PermissionsMixin


class BasePermissionsMixin(PermissionsMixin):
    """
    Abstract base class for permissions mixins to ease typing annotations.

    PermissionMixins are used to alter authorization flow. To use it, add
    it to classes from which your user model is inherited.

    e.g: -------------------------- User(AbstractUser, BasePermissionMixin):
                                       pass
    """

    class Meta:
        abstract = True


class NoGroupsMixin(PermissionsMixin):
    """
    Disables default flow of group permissions.
    It works like every user is in every group.

    If used with NoUserPermissionsMixin, user won't have any permissions.
    """

    groups = None

    class Meta:
        abstract = True


class NoUserPermissionsMixin(PermissionsMixin):
    """
    Deletes user_permissions field from user model.
    """

    user_permissions = None

    class Meta:
        abstract = True


class NoAccessControlMixin(NoGroupsMixin, NoUserPermissionsMixin):
    """
    /
    """

    class Meta:
        abstract = True


class NoStaffMixin(PermissionsMixin):
    """
    Deletes concept of superuser from authorization flow.
    Every user is basically a staff user now.
    """

    is_staff = True

    class Meta:
        abstract = True


class NoSuperuser(PermissionsMixin):
    """
    Deletes concept of superuser from authorization flow.
    Every user is basically a superuser now.
    """

    is_superuser = True

    class Meta:
        abstract = True


class GroupBasedStaffMixin:
    """
    Modifies user model so is_staff is implemented
    with groups and not with binary field.
    """

    is_staff = None

    @property
    def is_staff(self) -> bool:
        pass

    @is_staff.setter
    def is_staff(self, value: bool) -> None:
        pass

    class Meta:
        abstract = True


class GroupBasedSuperuserMixin:
    """
    Modifies user model so is_superuser is implemented
    with groups and not with binary field.
    """

    is_superuser = None

    @property
    def is_superuser(self) -> bool:
        pass

    @is_superuser.setter
    def is_superuser(self, value: bool) -> None:
        pass

    class Meta:
        abstract = True
