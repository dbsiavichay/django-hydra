""" Hydra list view """
# Python
import operator
from functools import reduce

# Django
from django.views.generic import View
from django.views.generic import ListView as BaseListView

# Mixins
#from hydra.mixins import MultiplePermissionRequiredModelMixin

# Hydra
from hydra.views import get_base_view
from hydra.shortcuts import get_urls_of_site

# Utilities
from hydra.utils import (
    get_field_label_of_model,
    get_attribute_of_instance,
)


class ListMixin:
    """Definimos la clase que utilizará el modelo"""

    """
    permission_autosite = (
        f"{self.model._meta.app_label}.view_{self.model._meta.model_name}",
        f"{self.model._meta.app_label}.add_{self.model._meta.model_name}",
        f"{self.model._meta.app_label}.change_{self.model._meta.model_name}",
    )
    permission_required = permission_autosite + self.permission_extra
    """

    action = "list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        opts = {
            "model_verbose_name_plural": self.model._meta.verbose_name_plural,
            "model": self.model,
            "order_by": self._get_headers(),
            "header_list": self._get_headers(),
            "row_list": self._get_rows(context["object_list"]),
            "count_list_start":context["page_obj"].start_index() if context["paginator"] else 1,
            "count_list_end":context["page_obj"].end_index() if context["paginator"] else context["object_list"].count(),
            "count_list": context["paginator"].count if context["paginator"] else context["object_list"].count(),
            "search_fields": self._get_search_fields_with_labels(),
            "active_searches": self._clean_search_params(),
        }

        if "site" in context:
            context["site"].update(opts)
        else:
            context.update({
                "site": opts
            })
    
        return context

    def reduce_queryset(self, params, queryset, op):
        args = []
        for field, value, verbose_name in params:
            action = '__icontains'
            if self.model._meta.get_field(field).__class__.__name__ in (
                'CharField',
                'TextField',
            ):
                action = '__unaccent' + action
            args.append(Q(**{field + action: value}))
        if args:
            queryset = queryset.filter(reduce(op, args))
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()

        params = self._clean_search_params()
        if 'sf' in self.request.GET:
            return self.reduce_queryset(params, queryset, operator.__or__)

        queryset = self.reduce_queryset(params, queryset, operator.__and__)
        return queryset

    def _get_headers(self):
        for name in self.site.list_fields:
            yield get_field_label_of_model(self.model, name)

    def _get_rows(self, queryset):
        for instance in queryset:
            urls = get_urls_of_site(self.site, instance)
            row = {
                'values_list': self._get_values(instance),
                **urls,
            }

            yield row

    def _get_values(self, instance):
        for name in self.site.list_fields:
            value = get_attribute_of_instance(instance, name)
            yield value

    ###Searching
    def _clean_search_params(self):
        params = []
        if 'sf' in self.request.GET:
            value = self.request.GET.get('sf')
            for field in self.site.search_fields:
                verbose_name = get_field_label_of_model(
                    self.site.model, '.'.join(field.split('__'))
                )
                params.append((field, value, verbose_name))
            return params

        for key in self.request.GET.keys():
            if key.startswith('sf_') and key[3:] in self.site.search_fields:
                field = key[3:]
                verbose_name = get_field_label_of_model(
                    self.site.model, '.'.join(field.split('__'))
                )
                params.append((field, self.request.GET.get(key), verbose_name))
        return params

    def _get_search_fields_with_labels(self):
        fields = []
        for field in self.site.search_fields:
            point_field = '.'.join(field.split('__'))
            fields.append(
                (
                    f'sf_{field}',
                    get_field_label_of_model(self.model, point_field),
                )
            )
        return fields



class ListView(View):
    site = None

    def view(self, request, *args, **kwargs):
        """ Crear la List View del modelo """
        # Class
        View = get_base_view(BaseListView, ListMixin, self.site)
        
        # Set attriburtes
        View.queryset = self.site.queryset
        View.paginate_by = self.site.paginate_by

        View.__bases__ = (*self.site.list_mixins, *View.__bases__)

        view = View.as_view()
        return view(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.view(request, *args, **kwargs)
