""" """
# Django
from django.views.generic import View
from django.views.generic import DeleteView as BaseDeleteView

# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

# Hydra
from hydra.views import get_base_view
from hydra.shortcuts import get_urls_of_site

class DeleteMixin:
    """Definimos la clase que utilizará el modelo"""

    """
    permission_required = (
        f'{self.model._meta.app_label}.delete_{self.model._meta.model_name}',
    )
    """
    action = "delete"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        opts = {
            "model_verbose_name_plural": self.model._meta.verbose_name_plural,
            **get_urls_of_site(self.site, self.object),
        }

        if "site" in context:
            context["site"].update(opts)
        else:
            context.update({
                "site": opts
            })
        return context

    def get_success_url(self):
        return get_urls_of_site(self.site, self.object).get('list_url')


class DeleteView(View):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        View = get_base_view(BaseDeleteView, DeleteMixin, self.site)
        
        # Set attribures

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)

