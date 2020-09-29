""" """
# Django
from django.views.generic import View
from django.views.generic import DetailView as BaseDetailView

# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

# Hydra
from hydra.views import get_base_view
from hydra.shortcuts import get_urls_of_site

from hydra.utils import (
    get_field_label_of_model,
    get_attribute_of_instance,
)

class DetailMixin:
    """Definimos la clase que utilizará el modelo"""

    """
    permission_autosite = (
        f'{self.model._meta.app_label}.view_{self.model._meta.model_name}',
        f'{self.model._meta.app_label}.add_{self.model._meta.model_name}',
        f'{self.model._meta.app_label}.change_{self.model._meta.model_name}',
    )
    permission_required = permission_autosite + self.permission_extra
    """

    action = "detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        opts = {
            "model_verbose_name_plural": self.model._meta.verbose_name_plural,
            "results": self._get_results(),
            **get_urls_of_site(self.site, self.object),
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
            label = get_field_label_of_model(self.object, field)
            value = get_attribute_of_instance(self.object, field)
            yield (label, value)


class DetailView(View):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        View = get_base_view(BaseDetailView, DetailMixin, self.site)

        # Set attributes

        View.__bases__ = (*self.site.detail_mixins, *View.__bases__)

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)
