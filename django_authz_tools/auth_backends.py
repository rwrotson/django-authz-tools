from django.contrib.auth import get_user_model


UserModel = get_user_model()


class BaseBackend:
    def authenticate(self, request, **kwargs):
        return None

    def get_user(self, user_id):
        return None

    def get_user_permissions(self, user_obj, obj=None) -> set:
        return set()

    def get_group_permissions(self, user_obj, obj=None) -> set:
        return set()

    def get_all_permissions(self, user_obj, obj=None) -> set[]:
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_group_permissions(user_obj, obj=obj),
        }

    def has_perm(self, user_obj, perm, obj=None) -> bool:
        return perm in self.get_all_permissions(user_obj, obj=obj)
