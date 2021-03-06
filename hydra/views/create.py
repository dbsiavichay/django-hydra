""" """
# Django
from django.views.generic import View
from django.views.generic import CreateView as BaseCreateView
from django.forms.models import model_to_dict

# Mixins
#from .mixins import BreadcrumbMixin, TemplateMixin

# Hydra
from .base import get_base_view
from hydra.shortcuts import get_object
from hydra.utils import import_all_mixins


class CreateMixin:
    """Definimos la clase que utilizará el modelo"""
    #permission_required = permission_autosite + self.permission_extra

    action = "create"
    duplicate_param = "duplicate"


    def get_related_initial(self, object):
        related_initial = {}
        for related in object._meta.related_objects:
            related_name = related.related_name
            related_name = related_name if related_name else f'{related.name}_set'
            related_objects = [
                model_to_dict(
                    obj, fields=[
                        field.name for field in obj._meta.fields 
                        if field.name!='id' and field.name!=related.remote_field.name
                    ]
                ) 
                for obj in getattr(object, related_name).all()
            ]
            related_initial.update({
                related.related_model: related_objects
            })

        return related_initial

    def get_initial(self):
        initial = super().get_initial()
        if self.request.method == 'GET':
            slug_or_pk = self.request.GET.get(self.duplicate_param)
            if slug_or_pk:
                object = get_object(self.model, slug_or_pk)
                if object:
                    data = model_to_dict(
                        object, fields=[field.name for field in object._meta.fields if field.name!='id']
                    )
                    initial.update(data)
                    initial['related_initial'] = self.get_related_initial(object)
        return initial


class CreateView(View):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        mixins = import_all_mixins() + [CreateMixin]
        View = get_base_view(BaseCreateView, mixins, self.site)

        # Set attributes
        View.form_class = self.site.form_class
        View.fields = self.site.fields

        View.__bases__ = (*self.site.form_mixins, *View.__bases__)
        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)
