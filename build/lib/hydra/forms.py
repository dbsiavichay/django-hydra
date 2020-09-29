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


class ModelFormOptions(DjangoModelFormOptions):
    def __init__(self, options=None):
        super().__init__(options)
        self.fieldsets = getattr(options, 'fieldsets', None)


class ModelFormMetaclass(DjangoModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        new_class._meta  = ModelFormOptions(getattr(new_class, 'Meta', None))
        return new_class


class FieldsetsModelForm(BaseModelForm, metaclass=ModelFormMetaclass):
    @classmethod
    def fields_for_model(cls, fieldsets):
        fields = list()
        for fieldset in fieldsets:
            if isinstance(fieldset, tuple):
                fields += [field for field in fieldset]
            else:
                fields.append(fieldset)
        return tuple(fields)

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
