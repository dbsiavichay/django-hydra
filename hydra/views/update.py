""" """
# Django
from django.views.generic import View
from django.views.generic import UpdateView as BaseUpdateView


# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

# Hydra
from .base import get_base_view
from hydra.shortcuts import get_urls_of_site


class UpdateMixin:
    """Update View del modelo"""

    action = "update"

class UpdateView(View):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        View = get_base_view(BaseUpdateView, UpdateMixin, self.site)

        # Set attribures
        View.form_class = self.site.form_class
        View.fields = self.site.fields

        View.__bases__ = (*self.site.form_mixins, *View.__bases__)

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)