from typing import Literal

from django.db.models import QuerySet, Model, Exists, OuterRef, Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import (
    ModelBackend as DefaultModelBackend,
    AllowAllUsersModelBackend as DefaultAllowAllUsersModelBackend,
    RemoteUserBackend as DefaultRemoteUserBackend,
    AllowAllUsersRemoteUserBackend as DefaultAllowAllUsersRemoteUserBackend,
)
from django.contrib.auth.models import Permission as DefaultPermission
from allauth.account.auth_backends import AuthenticationBackend as DefaultAuthenticationBackend

from django_authz_tools.helpers.model_utils import get_permission_model


UserModel = get_user_model()
PermissionModel = get_permission_model()


class ModelBackend(DefaultModelBackend):
    """
    Patched backend from django.contrib.auth.backends.

    Authenticates against settings.AUTH_USER_MODEL.
    """

    def _get_group_permissions(self, user_obj: UserModel) -> QuerySet[PermissionModel]:
        user_groups = getattr(user_obj, "groups", [])
        return PermissionModel.objects.filter(group__in=user_groups)

    def _get_permissions(
        self,
        user_obj: UserModel,
        obj: Model | None,
        from_name: Literal["user", "group"],
    ) -> set:
        """
        Return the permissions of `user_obj` from `from_name`. `from_name` can
        be either "group" or "user" to return permissions from
        `_get_group_permissions` or `_get_user_permissions` respectively.
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        perm_cache_name = "_%s_perm_cache" % from_name
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = PermissionModel.objects.all()
            else:
                perms = getattr(self, "_get_%s_permissions" % from_name)(user_obj)
            # perms = perms.values_list("content_type__app_label", "codename").order_by()
            # setattr(
            #     user_obj, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms}
            # )
        return getattr(user_obj, perm_cache_name)

    def with_perm(
        self,
        perm: PermissionModel | str,
        is_active: bool = True,
        include_superusers: bool = True,
        obj: Model | None = None,
    ) -> QuerySet[UserModel]:
        """
        Return users that have permission "perm". By default, filter out
        inactive users and include superusers.
        """
        if isinstance(perm, str):
            if perm.count(".") != 1:
                raise ValueError(
                    "Permission name should be in the form "
                    "app_label.permission_codename."
                )
        elif not isinstance(perm, PermissionModel):
            raise TypeError(
                "The `perm` argument must be a string or "
                "a permission instance inherited from BasePermission."
            )

        if obj is not None:
            return UserModel._default_manager.none()  # noqa

        permission_q = Q(group__user=OuterRef("pk")) | Q(user=OuterRef("pk"))
        if isinstance(perm, str):
            app_label, codename = perm.split(".")
            permission_q &= Q(codename=codename, content_type__app_label=app_label)
        elif isinstance(perm, DefaultPermission):
            pass
        else:  # isinstance(perm, PermissionModel) is True
            permission_q &= Q(pk=perm.pk)

        user_q = Exists(PermissionModel.objects.filter(permission_q))
        if include_superusers:
            user_q |= Q(is_superuser=True)
        if is_active is not None:
            user_q &= Q(is_active=is_active)

        return UserModel._default_manager.filter(user_q)  # noqa


class AllowAllUsersModelBackend(DefaultAllowAllUsersModelBackend, ModelBackend):
    """
    Patched backend from django.contrib.auth.backends.
    """
    pass


class RemoteUserBackend(DefaultRemoteUserBackend, ModelBackend):
    """
    Patched backend from django.contrib.auth.backends.
    """
    pass


class AllowAllUsersRemoteUserBackend(DefaultAllowAllUsersRemoteUserBackend, RemoteUserBackend):
    """
    Patched backend from django.contrib.auth.backends.
    """
    pass


class AuthenticationBackend(DefaultAuthenticationBackend, ModelBackend):
    """
    Patched all-auth authentication backend from allauth.account.auth_backends.
    """
    pass
