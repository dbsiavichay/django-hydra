"""Mixins for autosite"""

# Django
from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.contrib import messages

#Utils
from .utils import get_label_of_field


class FormsetList:
    formsets = dict()

    """
    formsets = {
        "invoice_formset": Formset
    }
    """

    def __init__(self, formsets):
        self.formsets = dict()

        for key, formset_class in formsets.items():
            headers = [
                get_label_of_field(formset_class.form.Meta.model, field_name)
                for field_name in formset_class.form.Meta.fields
            ]
            self.formsets.update({
                key: {
                    "class": formset_class,
                    "headers": headers
                }
            })

    def is_valid(self):
        errors = [fs["instance"].errors for fs in self.formsets.values() if not fs["instance"].is_valid()]
        return not errors

    def get_headers(self):
        headers = {
            f"{key}_headers": value["headers"]
            for key, value in self.formsets.items()
        }
        return headers

    def get_instances(self, **kwargs):
        for key in self.formsets:
            formset_class = self.formsets[key]["class"]
            instance = formset_class(**kwargs)
            self.formsets.get(key).update({
                "instance": instance,
            })

        instances = {
            key: value["instance"]
            for key, value in self.formsets.items()
        }
        return instances

    def get_formset(self, name):
        return self.formsets[name]["instance"]

"""
class FormsetMixin:

    formset = None

    def get_context_data(self, **kwargs):
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
        return self.formset(**self.get_form_kwargs())
"""

class FormsetMixin:
    """Class for add multiple formsets in form"""

    formsets = dict()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.formsets = FormsetList(formsets=self.formsets)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        formsets = self.get_formsets()
        headers = self.get_headers()
        context.update(
            **formsets, **headers
        )
        return context

    def formsets_valid(self, formsets, form):
        with transaction.atomic():
            self.object = form.save()
            for formset in formsets:
                formset.instance = self.object
                formset.save()

        messages.success(self.request, "Se ha guardado correctamente.")
        return redirect(self.get_success_url())

    def formsets_invalid(self, formsets, form):
        for formset in formsets:
            for error in formset.errors:
                form.errors.update(error)
        return super().form_invalid(form)

    def get_headers(self):
        headers = self.formsets.get_headers()
        return headers

    def get_formsets(self):
        """Method to get all formsets"""
        formsets = self.formsets.get_instances(**self.get_form_kwargs())
        return formsets

    def get_formset(self, name):
        return self.formsets.get_formset(name)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() if self.action == "update" else None
        form = self.get_form()
        formsets = self.get_formsets().values()

        if self.formsets.is_valid() and form.is_valid():
            return self.formsets_valid(formsets, form)
        else:
            return self.formsets_invalid(formsets, form)



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
