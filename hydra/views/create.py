""" """
# Python
import copy

# Django
from django.views.generic import View
from django.views.generic import CreateView as BaseCreateView

# Mixins
#from .mixins import BreadcrumbMixin, TemplateMixin

# Hydra
from .base import get_base_view
from hydra.shortcuts import get_urls_of_site

class CreateMixin:
    """Definimos la clase que utilizará el modelo"""
    #permission_required = permission_autosite + self.permission_extra

    action = "create"

class CreateView(View):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        View = get_base_view(BaseCreateView, CreateMixin, self.site)

        # Set attributes
        View.form_class = self.site.form_class
        View.fields = self.site.fields

        View.__bases__ = (*self.site.form_mixins, *View.__bases__)

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)
