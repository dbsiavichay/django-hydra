""" Forms for menu """
# Python
import inspect

# Django
from django.forms import ModelForm, BaseModelForm, ChoiceField
from django.forms.utils import ErrorList
from django.forms.models import ModelFormOptions as DjangoModelFormOptions
from django.forms.models import ModelFormMetaclass as DjangoModelFormMetaclass
from django.views.generic import View
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

# Models
from .models import Action, Menu


class ActionForm(ModelForm):
    element = ChoiceField(
        label="Elemento"
    )

    class Meta:
        model = Action
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ct = ContentType.objects.get_for_model(Permission)
        codenames = ("add_permission","change_permission","delete_permission","view_permission")
        queryset = Permission.objects.filter(content_type=ct).exclude(codename__in=codenames)
        self.fields["permissions"].queryset = queryset

        MODEL_CHOICES = [
            (
                model._meta.model_name,
                f"{app.verbose_name.capitalize()} | {model._meta.verbose_name.capitalize()}"
            )
            for app in apps.get_app_configs() for model in app.get_models()
        ]

        app_list = [app for app in apps.get_app_configs() if hasattr(app.module, "views")]
        VIEWS_CHOICES = [
            (
                name,
                f"{app.verbose_name.capitalize()} | {name}"
            )
            for app in app_list for name, view in inspect.getmembers(app.module.views, inspect.isclass)
            if issubclass(view, View)
        ]

        self.fields["element"].choices = MODEL_CHOICES + VIEWS_CHOICES


class MenuForm(ModelForm):
    class Meta:
        model = Menu
        exclude = ('route',)

    def save(self, commit=True):
        menu = super().save(commit=False)
        menu.route = str(menu)
        if commit:
            menu.save()
        return menu


class PermissionForm(ModelForm):
    class Meta:
        model = Permission
        exclude = ("content_type",)

    def save(self, commit=True):
        perm = super().save(commit=False)
        ct = ContentType.objects.get_for_model(Permission)
        perm.content_type = ct
        if commit:
            perm.save()
        return perm


class ModelFormMetaclass(DjangoModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        fieldsets = None
        if "Meta" in attrs and hasattr(attrs["Meta"], "fieldsets"):
            fieldsets = attrs["Meta"].fieldsets
            fields = mcs.__fields__(fieldsets)
            if hasattr(attrs["Meta"], "fields"):
                fields = fields + attrs["Meta"].fields
            attrs["Meta"].fields = fields
        new_class = super().__new__(mcs, name, bases, attrs)
        if fieldsets:
            new_class._meta.fieldsets = fieldsets
        return new_class

    def __fields__(fieldsets):
        fields = list()
        for fieldset in fieldsets:
            if isinstance(fieldset, tuple):
                fields += [field for field in fieldset]
            else:
                fields.append(fieldset)
        return tuple(fields)


class ModelForm(BaseModelForm, metaclass=ModelFormMetaclass):
    def get_fieldsets(self):
        sets = list()
        for fieldset in self._meta.fieldsets:
            if isinstance(fieldset, tuple):
                sets.append({
                    'bs_cols': int(12 / len(fieldset)),
                    'fields': [self[field] for field in fieldset]
                })
            else:
                sets.append({
                    'bs_cols': 12,
                    'fields': [self[fieldset]]
                })
        return sets

    def has_fieldsets(self):
        return hasattr(self._meta, "fieldsets")
