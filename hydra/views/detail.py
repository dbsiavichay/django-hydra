""" """
# Django
from django.views.generic import View
from django.views.generic import DetailView as BaseDetailView

# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

# Hydra
from .base import get_base_view
from hydra.shortcuts import get_urls_of_site

from hydra.utils import (
    get_label_of_field,
    get_attr_of_object,
    import_all_mixins
)

class DetailMixin:
    """Definimos la clase que utilizará el modelo"""

    action = "detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        opts = {
            "results": self._get_results(),
            "urls": get_urls_of_site(self.site, self.object),
        }

        if "site" in context:
            context["site"].update(opts)
        else:
            context.update({
                "site": opts
            })

        return context

    def _get_results(self):
        fields = (
            self.site.detail_fields
            if self.site.detail_fields
            else (field.name for field in self.model._meta.fields)
        )
        for field in fields:
            label = get_label_of_field(self.object, field)
            value = get_attr_of_object(self.object, field)
            yield (label, value)


class DetailView(View):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        mixins = import_all_mixins() + [DetailMixin]
        View = get_base_view(BaseDetailView, mixins, self.site)

        # Set attributes
        View.__bases__ = (*self.site.detail_mixins, *View.__bases__)

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)
