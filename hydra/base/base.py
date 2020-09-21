"""Classes and functios for register site models"""

import operator
from functools import reduce

# Django
#from django.db.models import Q
#from django.shortcuts import redirect
from django.utils.text import slugify
#from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db.models.base import ModelBase
#from django.forms.utils import pretty_name
from django.urls import path, include #reverse_lazy, reverse
from django.utils.html import format_html

# Utilities
#from hydra.utils import (
    #get_project_path,
    #inspect_clases,
    #get_installed_apps,
#)

from hydra.urls import get_module_urls


# Views
from hydra.views import BaseView, ModuleView, get_app_view
from .list import ListView
from .create import CreateView
from .update import UpdateView
from .detail import DetailView
from .delete import DeleteView

# Utils
from hydra.utils import import_class


class ModelSite:
    """Superclass that generate CRUD Views for any model"""

    #Views
    model = None
    form_class = None # Used for create Create and Update views
    fields = None # User for passed to Create and Update views for generate forms
    fieldsets = () # Used for generate group of fields
    list_display = ("__str__",) # Used for create ListView with de specified fields
    detail_display = () # Used for create DetailView with specified fields
    views_display = "list", "form", "detail", "delete" # Says Hydra which views create

    # Templates
    list_template_name = None # Says Hydra which list template use
    form_template_name = None # Says Hydra which form template use
    detail_template_name = None # Says Hydra which detail template use
    delete_template_name = None # Says Hydra which delete template use

    # Mixins
    list_mixins = () # List of mixins that Hydra include in ListViews
    form_mixins = () # List of mixins that Hydra include in Create and Update Views
    detail_mixins = () # List of mixins that Hydra include in DetailViews

    # Permissions
    permission_extra = ()
    
    # Options for build queryset
    queryset = None # Specified custom queryset
    paginate_by = None # Specified if ListView paginated by

    # Filter and ordering
    search_fields = () #Used for create searchs method by specified fields
    order_by = () #User for crate ordering methods by specified fields

    # Urls
    url_list_suffix = "list"
    url_create_suffix = "create"
    url_update_suffix = "update"
    url_detail_suffix = "detail"
    url_delete_suffix = "delete"

    # Routes
    routes = ()

    # Breadcrumbs
    breadcrumb_home_text = "Home"
    breadcrumb_create_text = "Create"
    breadcrumb_update_text = "Update"
    breadcrumb_detail_text = None
    breadcrumb_delete_text = "Delete"

    @classmethod
    def get_info(cls):
        """Obtiene la información del modelo"""
        #info = cls.model._meta.app_label, cls.model._meta.model_name
        info = slugify(cls.model._meta.app_config.verbose_name), slugify(cls.model._meta.verbose_name)
        return info

    @classmethod
    def get_base_url_name(cls, suffix):
        info = cls.get_info()
        url_suffix = getattr(cls, "url_%s_suffix" % suffix)
        base_url_name = "%s_%s_%s" % (*info, url_suffix)
        return base_url_name

    @classmethod
    def get_url_name(cls, suffix):
        url_name = "site:%s" % cls.get_base_url_name(suffix)
        return url_name

    def get_breadcrumb_text(self, name):
        text = getattr(self, "breadcrumb_%s_text" % name)
        if not text: return None
        return format_html(text)

    def get_urls(self, route):
        """Genera las urls para los modelos registrados"""

        # def wrap(view):
        #     def wrapper(*args, **kwargs):
        #         return self.admin_site.admin_view(view)(*args, **kwargs)
        #     wrapper.model_admin = self
        #     return update_wrapper(wrapper, view)
        urlpatterns = []

        if not isinstance(self.views_display, tuple):
            raise ImproperlyConfigured('El campo <views_display> debe ser una tupla.')

        if "list" in self.views_display:
            #url_name = "%s_%s_%s" % (*info, self.url_list_suffix)
            url_name = self.get_base_url_name("list")
            urlpatterns += [
                path(
                    route = f"{route}/", 
                    view = ListView.as_view(site=self), 
                    name = url_name
                )
            ]

        if "form" in self.views_display:
            url_create_name = self.get_base_url_name("create")
            url_update_name = self.get_base_url_name("update")

            urlpatterns += [
                path(
                    route = f"{route}/{self.url_create_suffix}/", 
                    view = CreateView.as_view(site=self), 
                    name = url_create_name
                ),
                path(
                    route = f"{route}/<int:pk>/{self.url_update_suffix}/", 
                    view = UpdateView.as_view(site=self), 
                    name = url_update_name
                ),
                path(
                    route = f"{route}/<slug:slug>/{self.url_update_suffix}/", 
                    view = UpdateView.as_view(site=self), 
                    name = url_update_name
                ),
            ]
        
        if "detail" in self.views_display:
            url_detail_name = self.get_base_url_name("detail")

            urlpatterns += [
                path(
                    route = f"{route}/<int:pk>/{self.url_detail_suffix}/", 
                    view = DetailView.as_view(site=self), 
                    name = url_detail_name
                ),
                path(
                    route = f"{route}/<slug:slug>/{self.url_detail_suffix}/", 
                    view = DetailView.as_view(site=self), 
                    name = url_detail_name
                ),
            ]

        if "delete" in self.views_display:
            url_delete_name = self.get_base_url_name("delete")

            urlpatterns += [
                path(
                    route = f"{route}/<int:pk>/{self.url_delete_suffix}/",
                    view = DeleteView.as_view(site=self), 
                    name = url_delete_name
                ),
                path(
                    route = f"{route}/<slug:slug>/{self.url_delete_suffix}/",
                    view = DeleteView.as_view(site=self),
                    name = url_delete_name,
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
        urlpatterns = []
        if not self.routes:
            self.routes = ["%s/%s" % self.get_info()]
        for route in self.routes:
            urlpatterns.extend(self.get_urls(route))
        return urlpatterns

   
class Site:
    """Site class"""

    _registry = {}
    name = 'site'

    def register(self, model_or_iterable, site_class=None, **options):
        """Registra las clases en el auto site"""

        site_class = site_class or ModelSite
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    'The model %s is abstract, so it cannot be registered with hydra.'
                    % model.__name__
                )

            if model in self._registry:
                raise Exception('The model %s is already registered' % model.__name__)

            Menu = import_class("hydra.models", "Menu")
            ContentType = import_class("django.contrib.contenttypes.models", "ContentType")
            content_type = ContentType.objects.get_for_model(model)
            routes = Menu.objects.filter(content_type=content_type).values_list("route", flat=True)
            site_class.routes = routes
            print("Call to db Menus routes")

            self._registry[model] = site_class()

    def get_urls(self):
        """Obtiene las urls de auto site"""

        # def wrap(view, cacheable=False):
        #   def wrapper(*args, **kwargs):
        #       return self.admin_view(view, cacheable)(*args, **kwargs)
        #       wrapper.admin_site = self
        #       return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = get_module_urls()

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        for model, model_site in self._registry.items():
            #info = (model._meta.app_label, slugify(model._meta.verbose_name))
            #if not model_site.routes:
            #    info = model_site.get_info()
            #    url_format = "%s/%s/" % info
            #    urlpatterns += [path(url_format, include(model_site.urls))]
            #else:
            urlpatterns.extend(model_site.urls)

        return urlpatterns

    @property
    def urls(self):
        """Permite registrar las URLs en el archivo de urls del proyecto"""
        return self.get_urls(), 'site', self.name


site = Site()
