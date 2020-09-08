"""Mixins for autosite"""
from django.contrib.auth.mixins import PermissionRequiredMixin


class MultiplePermissionRequiredModuleMixin(PermissionRequiredMixin):
    """Verifica los permisos de acceso al módulo"""

    def has_permission(self):
        user = self.request.user
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return True
        permissions = list()
        ctx = self.get_context_data()
        for model in ctx["models_permissions"]:
            permissions.append(f"{model._meta.app_label}.view_{model._meta.model_name}")
            permissions.append(f"{model._meta.app_label}.add_{model._meta.model_name}")
            permissions.append(
                f"{model._meta.app_label}.change_{model._meta.model_name}"
            )
        return any(user.has_perm(permission) for permission in permissions)


class MultiplePermissionRequiredAppMixin(MultiplePermissionRequiredModuleMixin):
    """Verifica los permisos de acceso a la app"""


class MultiplePermissionRequiredModelMixin(PermissionRequiredMixin):
    """Verifica los permisos de acceso al modelo"""

    def has_permission(self):
        user = self.request.user
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return True
        permissions = self.permission_required
        return any(user.has_perm(permission) for permission in permissions)
