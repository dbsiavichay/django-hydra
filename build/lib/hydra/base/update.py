""" """
# Django
from django.views.generic import View 
from django.views.generic import UpdateView as BaseUpdateView


# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

# Hydra
from hydra.views import get_base_view
from hydra.shortcuts import get_urls_of_site


class UpdateMixin:
    """Update View del modelo"""

    """
    permission_autosite = (
        f'{self.model._meta.app_label}.change_{self.model._meta.model_name}',
    )
    permission_required = permission_autosite + self.permission_extra
    """
    action = "update"

    def get_success_url(self):
        return get_urls_of_site(self.site, self.object).get('detail_url')


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