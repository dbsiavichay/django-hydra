"""Mixins for autosite"""

# Django
from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction

#Utils
from .utils import get_label_of_field


class FormsetMixin:
    """Class for add single formset in Form"""

    formset = None

    def get_context_data(self, **kwargs):
        """
        Args:
            **kwargs:
        """
        context = super().get_context_data(**kwargs)
        formset_headers = (
            get_label_of_field(self.formset.form._meta.model, field_name) 
            for field_name in self.formset.form._meta.fields
        )
        context.update({
            "formset_headers": formset_headers,
            "formset": self.get_formset()
        })
        return context

    def form_valid(self, form):
        formset = self.get_formset()
        with transaction.atomic():
            if formset.is_valid():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
            else:
                for error in formset.errors:
                    form.errors.update({**error})
                return self.form_invalid(form)
        return redirect(self.get_success_url())

    def get_formset(self):
        """Function to get formset"""
        return self.formset(**self.get_form_kwargs())


class MultipleFormsetMixin:
    """Class for add multiple formsets in form"""

    formsets = ()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "formsets": self.get_formsets()
        })
        return context

    
    def form_valid(self, form):
        formsets = self.get_formsets()
        errors = (fs.errors for fs in formsets if not fs.is_valid())

        with transaction.atomic():
            if not errors:
                self.object = form.save()
                for formset in formsets:
                    formset.instance = self.object
                    formset.save()
            else:
                for error in errors:
                    form.errors.update({**error})
                return self.form_invalid(form)

        return redirect(self.get_success_url())
    

    def get_formsets(self):
        """Method to get all formsets"""
        formsets = [formset(**self.get_form_kwargs()) for formset in self.formsets]
        return formsets



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
