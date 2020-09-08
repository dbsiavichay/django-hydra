"""Classes and functios for register site models"""

import operator
from functools import reduce

# Django
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.text import slugify
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models.base import ModelBase
from django.forms.utils import pretty_name
from django.urls import include, path, reverse_lazy, reverse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
)

# Utilities
from .utils import (
    get_project_path,
    inspect_clases,
    get_installed_apps,
    get_field_label_of_model,
    get_attribute_of_instance,
)

# Views
from hydra.views import BaseView, ModuleView, get_app_view


class ModelSite:
    """Clase que sirve para registrar los modelos, añadiendo las vistas de Create, Update, List y Detail"""

    model = None
    form_class = None
    list_display = ("__str__",)
    detail_display = ()
    views_display = "form", "detail", "delete"
    search_fields = ()
    list_template_name = None
    form_template_name = None
    detail_template_name = None
    delete_template_name = None
    list_mixins = ()
    form_mixins = ()
    detail_mixins = ()
    delete_field = None
    queryset = None
    paginate_by = None
    order_by = ()
    prefix_url = ""
    prefix_url_name = ""
    build_in_menu = True
    permission_extra = ()

    @classmethod
    def get_info(cls):
        """Obtiene la información del modelo"""
        info = cls.model._meta.app_label, cls.model._meta.model_name
        # info = cls.model._meta.app_label, slugify(cls.model._meta.verbose_name)
        return info

    def get_urls(self):
        """Genera las urls para los modelos registrados"""

        # def wrap(view):
        #     def wrapper(*args, **kwargs):
        #         return self.admin_site.admin_view(view)(*args, **kwargs)
        #     wrapper.model_admin = self
        #     return update_wrapper(wrapper, view)

        info = self.get_info()

        urlpatterns = [path("", self.list_view, name="%s_%s_list" % info)]

        if not isinstance(self.views_display, tuple):
            raise ImproperlyConfigured("El campo <views_display> debe ser una tupla.")

        if "form" in self.views_display:
            urlpatterns += [
                path("crear/", self.create_view, name="%s_%s_crear" % info),
                path("<int:pk>/editar/", self.update_view, name="%s_%s_editar" % info),
                path(
                    "<slug:slug>/editar/", self.update_view, name="%s_%s_editar" % info
                ),
            ]

        if "detail" in self.views_display:
            urlpatterns += [
                path("<int:pk>/", self.detail_view, name="%s_%s_detalle" % info),
                path("<slug:slug>/", self.detail_view, name="%s_%s_detalle" % info),
            ]

        if "delete" in self.views_display:
            urlpatterns += [
                path(
                    "<int:pk>/eliminar/", self.delete_view, name="%s_%s_eliminar" % info
                ),
                path(
                    "<slug:slug>/eliminar/",
                    self.delete_view,
                    name="%s_%s_eliminar" % info,
                ),
            ]

        # urlpatterns = [
        # path('add/', wrap(self.add_view), name='%s_%s_add' % info),
        # path('autocomplete/', wrap(self.autocomplete_view), name='%s_%s_autocomplete' % info),
        # path('<path:object_id>/history/', wrap(self.history_view), name='%s_%s_history' % info),
        # path('<path:object_id>/delete/', wrap(self.delete_view), name='%s_%s_delete' % info),
        # path('<path:object_id>/change/', wrap(self.change_view), name='%s_%s_change' % info),
        # # For backwards compatibility (was the change url before 1.9)
        # path('<path:object_id>/', wrap(RedirectView.as_view(
        #     pattern_name='%s:%s_%s_change' % ((self.admin_site.name,) + info)
        # ))),
        # ]
        return urlpatterns

    @property
    def urls(self):
        """Retorna las urls creadas"""
        return self.get_urls()

    def list_view(self, request, *args, **kwargs):
        """Crear la List View del modelo"""
        from .mixins import MultiplePermissionRequiredModelMixin

        model_site = self

        class View(MultiplePermissionRequiredModelMixin, BaseView, ListView):
            """Definimos la clase que utilizará el modelo"""

            permission_autosite = (
                f"{self.model._meta.app_label}.view_{self.model._meta.model_name}",
                f"{self.model._meta.app_label}.add_{self.model._meta.model_name}",
                f"{self.model._meta.app_label}.change_{self.model._meta.model_name}",
            )
            permission_required = permission_autosite + self.permission_extra

            model = self.model
            queryset = self.queryset
            template_name = self.list_template_name
            paginate_by = self.paginate_by
            list_display = self.list_display

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        "site": {
                            "model_verbose_name_plural": self.model._meta.verbose_name_plural,
                            "model": self.model,
                            "breadcumbs": self._get_list_breadcumbs(
                                model_site.prefix_url_name
                                if model_site.prefix_url and model_site.prefix_url_name
                                else model_site.prefix_url
                            ),
                            "order_by": self._get_headers(),
                            "header_list": self._get_headers(),
                            "row_list": self._get_rows(context["object_list"]),
                            "count_list_start":context["page_obj"].start_index() if context["paginator"] else 1,
                            "count_list_end":context["page_obj"].end_index() if context["paginator"] else context['object_list'].count(),
                            "count_list": context['paginator'].count if context['paginator'] else context['object_list'].count(),
                            "search_fields": self._get_search_fields_with_labels(),
                            "active_searches": self._clean_search_params(),
                            **self._get_action_urls(),
                        }
                    }
                )

                return context

            def reduce_queryset(self, params, queryset, op):
                args = []
                for field, value, verbose_name in params:
                    action = "__icontains"
                    if self.model._meta.get_field(field).__class__.__name__ in (
                        "CharField",
                        "TextField",
                    ):
                        action = "__unaccent" + action
                    args.append(Q(**{field + action: value}))
                if args:
                    queryset = queryset.filter(reduce(op, args))
                return queryset

            def get_queryset(self):
                queryset = super().get_queryset()

                params = self._clean_search_params()
                if "sf" in self.request.GET:
                    return self.reduce_queryset(params, queryset, operator.__or__)

                queryset = self.reduce_queryset(params, queryset, operator.__and__)
                return queryset

            def _get_headers(self):
                for name in self.list_display:
                    yield get_field_label_of_model(self.model, name)

            def _get_rows(self, queryset):
                for instance in queryset:
                    row = {
                        "values_list": self._get_values(instance),
                        **self._get_action_urls(instance=instance),
                    }

                    yield row

            def _get_values(self, instance):
                for name in self.list_display:
                    value = get_attribute_of_instance(instance, name)
                    yield value

            ###Searching
            def _clean_search_params(self):
                params = []
                if "sf" in self.request.GET:
                    value = self.request.GET.get("sf")
                    for field in model_site.search_fields:
                        verbose_name = get_field_label_of_model(
                            model_site.model, ".".join(field.split("__"))
                        )
                        params.append((field, value, verbose_name))
                    return params

                for key in self.request.GET.keys():
                    if key.startswith("sf_") and key[3:] in model_site.search_fields:
                        field = key[3:]
                        verbose_name = get_field_label_of_model(
                            model_site.model, ".".join(field.split("__"))
                        )
                        params.append((field, self.request.GET.get(key), verbose_name))
                return params

            def _get_search_fields_with_labels(self):
                fields = []
                for field in model_site.search_fields:
                    point_field = ".".join(field.split("__"))
                    fields.append(
                        (
                            f"sf_{field}",
                            get_field_label_of_model(self.model, point_field),
                        )
                    )
                return fields

        for mixin in self.list_mixins:
            View.__bases__ = (mixin,) + View.__bases__

        view = View.as_view()
        return view(request, *args, **kwargs)

    def create_view(self, request, *args, **kwargs):
        """Create View del modelo"""
        from .mixins import MultiplePermissionRequiredModelMixin

        model_site = self

        class View(MultiplePermissionRequiredModelMixin, BaseView, CreateView):
            """Definimos la clase que utilizará el modelo"""

            permission_autosite = (
                f"{self.model._meta.app_label}.add_{self.model._meta.model_name}",
            )
            permission_required = permission_autosite + self.permission_extra
            model = self.model
            template_name = self.form_template_name
            success_url = reverse_lazy("site:%s_%s_list" % self.get_info())

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        "site": {
                            "breadcumbs": self._get_create_breadcumbs(
                                model_site.prefix_url_name
                                if model_site.prefix_url and model_site.prefix_url_name
                                else model_site.prefix_url
                            )
                        }
                    }
                )
                return context

            def get_success_url(self):
                return self._get_action_urls(instance=self.object).get("detail_url")

        for mixin in self.form_mixins:
            View.__bases__ = (mixin,) + View.__bases__

        if self.form_class:
            View.form_class = self.form_class
        else:
            View.fields = "__all__"

        view = View.as_view()
        return view(request, *args, **kwargs)

    def update_view(self, request, *args, **kwargs):
        """Definimos la clase que utilizará el modelo"""
        from .mixins import MultiplePermissionRequiredModelMixin

        model_site = self

        class View(MultiplePermissionRequiredModelMixin, BaseView, UpdateView):
            """Update View del modelo"""

            permission_autosite = (
                f"{self.model._meta.app_label}.change_{self.model._meta.model_name}",
            )
            permission_required = permission_autosite + self.permission_extra
            model = self.model
            template_name = self.form_template_name
            success_url = reverse_lazy("site:%s_%s_list" % self.get_info())

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        "site": {
                            "breadcumbs": self._get_update_breadcumbs(
                                model_site.prefix_url_name
                                if model_site.prefix_url and model_site.prefix_url_name
                                else model_site.prefix_url
                            )
                        }
                    }
                )
                return context

            def get_success_url(self):
                return self._get_action_urls(instance=self.object).get("detail_url")

        for mixin in self.form_mixins:
            View.__bases__ = (mixin,) + View.__bases__

        if self.form_class:
            View.form_class = self.form_class
        else:
            View.fields = "__all__"

        view = View.as_view()
        return view(request, *args, **kwargs)

    def detail_view(self, request, *args, **kwargs):
        """Detail View"""
        from .mixins import MultiplePermissionRequiredModelMixin

        model_site = self

        class View(MultiplePermissionRequiredModelMixin, BaseView, DetailView):
            """Definimos la clase que utilizará el modelo"""

            permission_autosite = (
                f"{self.model._meta.app_label}.view_{self.model._meta.model_name}",
                f"{self.model._meta.app_label}.add_{self.model._meta.model_name}",
                f"{self.model._meta.app_label}.change_{self.model._meta.model_name}",
            )
            permission_required = permission_autosite + self.permission_extra
            model = self.model
            template_name = self.detail_template_name

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        "model_site": model_site,  # Por borrar
                        "site": {
                            "model_verbose_name_plural": self.model._meta.verbose_name_plural,
                            "breadcumbs": self._get_detail_breadcumbs(
                                model_site.prefix_url_name
                                if model_site.prefix_url and model_site.prefix_url_name
                                else model_site.prefix_url
                            ),
                            "results": self._get_results(),
                            **self._get_action_urls(instance=self.object),
                        },
                    }
                )
                return context

            def _get_results(self):
                fields = (
                    model_site.detail_display
                    if model_site.detail_display
                    else (field.name for field in self.model._meta.fields)
                )
                for field in fields:
                    label = get_field_label_of_model(self.object, field)
                    value = get_attribute_of_instance(self.object, field)
                    yield (label, value)

        for mixin in self.detail_mixins:
            View.__bases__ = (mixin,) + View.__bases__

        view = View.as_view()
        return view(request, *args, **kwargs)

    def delete_view(self, request, *args, **kwargs):
        """Delete View"""
        model_site = self
        from .mixins import MultiplePermissionRequiredModelMixin

        class View(MultiplePermissionRequiredModelMixin, BaseView, DeleteView):
            """Definimos la clase que utilizará el modelo"""

            permission_required = (
                f"{self.model._meta.app_label}.delete_{self.model._meta.model_name}",
            )

            model = self.model
            template_name = self.delete_template_name
            success_url = reverse_lazy("site:%s_%s_list" % self.get_info())

            def delete(self, request, *args, **kwargs):
                delete_field = model_site.delete_field

                if delete_field:
                    self.object = self.get_object()
                    if hasattr(self.object, delete_field):
                        setattr(self.object, delete_field, True)
                        self.object.save()
                    else:
                        raise ImproperlyConfigured(
                            f"No existe el campo <{delete_field}> para {self.model._meta.model_name.capitalize()}"
                        )
                    return redirect(self.get_success_url())

                return super().delete(request, *args, **kwargs)

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context.update(
                    {
                        "site": {
                            "model_verbose_name_plural": self.model._meta.verbose_name_plural,
                            "breadcumbs": self._get_delete_breadcumbs(
                                model_site.prefix_url_name
                                if model_site.prefix_url and model_site.prefix_url_name
                                else model_site.prefix_url
                            ),
                            # "results": self._get_results(),
                            **self._get_action_urls(instance=self.object),
                        }
                    }
                )
                return context

        view = View.as_view()
        return view(request, *args, **kwargs)


class Site:
    """Site class"""

    _registry = {}
    name = "site"

    def register(self, model_or_iterable, site_class=None, **options):
        """Registra las clases en el auto site"""

        site_class = site_class or ModelSite
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    "The model %s is abstract, so it cannot be registered with admin."
                    % model.__name__
                )

            if model in self._registry:
                raise Exception("The model %s is already registered" % model.__name__)

            self._registry[model] = site_class()

    def get_urls(self):
        """Obtiene las urls de auto site"""

        # def wrap(view, cacheable=False):
        #   def wrapper(*args, **kwargs):
        #       return self.admin_view(view, cacheable)(*args, **kwargs)
        #       wrapper.admin_site = self
        #       return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = self.get_modules_urls()

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        for model, model_site in self._registry.items():
            info = (model._meta.app_label, slugify(model._meta.verbose_name))
            if model_site.prefix_url:
                url_format = "%s/%s/%s/" % ((model_site.prefix_url,) + info)
            else:
                url_format = "%s/%s/" % info
            urlpatterns += [path(url_format, include(model_site.urls))]

        return urlpatterns

    @property
    def urls(self):
        """Permite registrar las URLs en el archivo de urls del proyecto"""
        return self.get_urls(), "site", self.name

    def get_modules_urls(self):
        """Obtiene las urls de los proyectos"""
        urls = []
        project_path = get_project_path()
        views = inspect_clases(f"{project_path}.views", ModuleView)

        for view in views:
            urls.append(
                path(f"{view.module_name}/", view.as_view(), name=f"{view.module_name}")
            )
            if hasattr(view, "app_template_name"):
                urls += self.get_apps_urls(
                    view.module_name, view.module_label, view.app_template_name
                )
        return urls

    def get_apps_urls(self, module_name, module_label, template_name):
        """Obtiene las urls de las apps"""
        urls = []
        apps = (app for app in get_installed_apps() if module_name in app.name)

        for app in apps:
            kwargs = {
                "app_route": app.name,
                "app_label": app.verbose_name,
                "template_name": template_name,
                "module_url": reverse_lazy(f"site:{module_name}"),
                "module_label": module_label,
            }
            View = get_app_view(**kwargs)
            urls.append(
                path(f"{module_name}/{app.label}/", View.as_view(), name=f"{app.label}")
            )
        return urls


site = Site()
