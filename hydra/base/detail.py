""" """
# Django
from django.views.generic import View as GenericView
from django.views.generic import DetailView as GenericDetailView

# Views
from hydra.views import BaseView

# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

from hydra.utils import (
    get_field_label_of_model,
    get_attribute_of_instance,
)

class View(BaseView, GenericDetailView):
        """Definimos la clase que utilizará el modelo"""

        """
        permission_autosite = (
            f'{self.model._meta.app_label}.view_{self.model._meta.model_name}',
            f'{self.model._meta.app_label}.add_{self.model._meta.model_name}',
            f'{self.model._meta.app_label}.change_{self.model._meta.model_name}',
        )
        permission_required = permission_autosite + self.permission_extra
        """
    
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context.update(
                {
                    #'site': site,  # Por borrar
                    'site': {
                        'model_verbose_name_plural': self.model._meta.verbose_name_plural,
                        'breadcumbs': self.get_detail_breadcrumbs(),
                        'results': self._get_results(),
                        **self._get_action_urls(instance=self.object),
                    },
                }
            )
            return context

        def _get_results(self):
            fields = (
                self.site.detail_display
                if self.site.detail_display
                else (field.name for field in self.model._meta.fields)
            )
            for field in fields:
                label = get_field_label_of_model(self.object, field)
                value = get_attribute_of_instance(self.object, field)
                yield (label, value)


class DetailView(GenericView):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        
        # Set attribures
        View.site = self.site
        View.model = self.site.model
        View.template_name = self.site.detail_template_name

        for mixin in self.site.detail_mixins:
            View.__bases__ = (mixin,) + View.__bases__

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)
