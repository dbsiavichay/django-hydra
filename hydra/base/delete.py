""" """
# Django
from django.views.generic import View as GenericView
from django.views.generic import DeleteView as GenericDeleteView

# Views
from hydra.views import BaseView

# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

class View(BaseView, GenericDeleteView):
            """Definimos la clase que utilizará el modelo"""

            """
            permission_required = (
                f'{self.model._meta.app_label}.delete_{self.model._meta.model_name}',
            )
            """

            #success_url = reverse_lazy('site:%s_%s_list' % self.get_info())

            def delete(self, request, *args, **kwargs):
                delete_field = site.delete_field

                if delete_field:
                    self.object = self.get_object()
                    if hasattr(self.object, delete_field):
                        setattr(self.object, delete_field, True)
                        self.object.save()
                    else:
                        raise ImproperlyConfigured(
                            f'No existe el campo <{delete_field}> para {self.model._meta.model_name.capitalize()}'
                        )
                    return redirect(self.get_success_url())

                return super().delete(request, *args, **kwargs)

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        'site': {
                            'model_verbose_name_plural': self.model._meta.verbose_name_plural,
                            'breadcumbs': self.get_delete_breadcrumbs(),
                            # 'results': self._get_results(),
                            **self._get_action_urls(instance=self.object),
                        }
                    }
                )
                return context


class DeleteView(GenericView):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        
        # Set attribures
        View.site = self.site
        View.model = self.site.model
        View.template_name = self.site.delete_template_name

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)

