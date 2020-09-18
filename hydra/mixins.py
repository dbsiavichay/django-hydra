"""Mixins for autosite"""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin

#Utils
from .utils import get_field_label_of_model


class FormsetMixin:
    """Class for add single formset in Form"""

    formset_class = None

    def get_context_data(self, **kwargs):
        """
        Args:
            **kwargs:
        """
        context = super().get_context_data(**kwargs)
        formset_headers = (
            get_field_label_of_model(self.formset_class.form._meta.model, field_name) 
            for field_name in self.formset_class.form._meta.fields
        )
        context.update({
            "formset_headers": formset_headers,
            "formset": self.get_formset()
        })
        return context

    """
    def form_valid(self, form):
        formset = self.get_formset()
        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
        return redirect(self.get_succes_url())
    """

    def get_formset(self):
        """Function to get formset"""
        return self.formset_class(**self.get_form_kwargs())


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
