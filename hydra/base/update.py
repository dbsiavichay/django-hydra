""" """
# Django
from django.views.generic import View as GenericView
from django.views.generic import UpdateView as BaseUpdateView


# Mixins
from .mixins import BreadcrumbMixin
#from hydra.mixins import MultiplePermissionRequiredModelMixin


class UpdateView(GenericView):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        class View(BreadcrumbMixin, BaseUpdateView):
            """Update View del modelo"""

            """
            permission_autosite = (
                f'{self.model._meta.app_label}.change_{self.model._meta.model_name}',
            )
            permission_required = permission_autosite + self.permission_extra
            """
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        'site': {
                            'breadcumbs': self.get_update_breadcrumbs()
                        }
                    }
                )
                return context

            def get_success_url(self):
                return self._get_action_urls(instance=self.object).get('detail_url')

        
        # Set attribures
        View.site = self.site
        View.model = self.site.model
        View.template_name = self.site.form_template_name
        View.form_class = self.site.form_class
        View.fields = self.site.fields

        View.__bases__ = tuple({*self.site.form_mixins, *View.__bases__})

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)