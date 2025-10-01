from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from apis.constants import ADMIN, SUPER_ADMIN, USER


class RoleRequiredMixin(AccessMixin):
    login_url = '/'
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superadmin():
            user_role = SUPER_ADMIN
        elif request.user.is_admin():
            user_role = ADMIN
        elif request.user.is_user():
            user_role = USER
        else:
            user_role = None

        if self.allowed_roles and user_role not in self.allowed_roles:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
