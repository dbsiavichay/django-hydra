""" Forms for menu """
# Django
from django.forms import ModelForm, BaseModelForm
from django.forms.utils import ErrorList
from django.forms.models import ModelFormOptions as DjangoModelFormOptions
from django.forms.models import ModelFormMetaclass as DjangoModelFormMetaclass

# Models
from .models import Menu

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


class ModelFormMetaclass(DjangoModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        fieldsets = None
        if "Meta" in attrs and hasattr(attrs["Meta"], "fieldsets"):
            fieldsets = attrs["Meta"].fieldsets
            attrs["Meta"].fields = mcs.__fields__(fieldsets)
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
