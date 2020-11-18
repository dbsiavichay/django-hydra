# Django
from django.core.exceptions import ImproperlyConfigured
from django.utils.text import slugify
from django.urls import path

# Views
from .views import (
    ListView, CreateView, UpdateView, DetailView, DeleteView,
    DuplicateView,
)

ALL_FIELDS = "__all__"


class ModelSite:
    """Superclass that generate CRUD Views for any model"""

    #Views
    model = None
    form_class = None # Used for create Create and Update views
    fields = None # User for passed to Create and Update views for generate forms
    list_fields = ("__str__",) # Used for create ListView with de specified fields
    detail_fields = () # Used for create DetailView with specified fields
    allow_views = "list", "create", "update", "detail", "delete" # Says Hydra which views create
    success_url = "list"

    # Templates
    list_template_name = None # Says Hydra which list template use
    form_template_name = None # Says Hydra which form template use
    detail_template_name = None # Says Hydra which detail template use
    delete_template_name = None # Says Hydra which delete template use

    # Mixins
    list_mixins = () # List of mixins that Hydra include in ListViews
    form_mixins = () # List of mixins that Hydra include in Create and Update Views
    detail_mixins = () # List of mixins that Hydra include in DetailViews

    # Prepopulate
    prepopulate_slug = ()
    
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
    url_duplicate_suffix = "duplicate"

    # Breadcrumbs
    breadcrumb_home_text = "Home"
    breadcrumb_create_text = "Create"
    breadcrumb_update_text = "Update"
    breadcrumb_detail_text = None
    breadcrumb_delete_text = "Delete"

    def __init__(self, model, **kwargs):
        self.model = model
        if not self.model:
            raise ImproperlyConfigured("The 'model' attribute must be specified.")

        if not isinstance(self.allow_views, tuple):
            raise ImproperlyConfigured("The 'allow_views' attribute must be a tuple.")

        if not self.form_class and not self.fields:
            self.fields = ALL_FIELDS

    @classmethod
    def get_info(cls):
        """Obtiene la información del modelo"""
        #info = cls.model._meta.app_label, cls.model._meta.model_name
        info = slugify(cls.model._meta.app_config.verbose_name), slugify(cls.model._meta.verbose_name)
        return info

    # Url methods
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

    def get_urls(self):
        """Genera las urls para los modelos registrados"""

        # def wrap(view):
        #     def wrapper(*args, **kwargs):
        #         return self.admin_site.admin_view(view)(*args, **kwargs)
        #     wrapper.model_admin = self
        #     return update_wrapper(wrapper, view)
        urlpatterns = []

        has_slug = hasattr(self.model, "slug")
        route_param = "<slug:slug>" if has_slug else "<int:pk>"

        if "list" in self.allow_views:
            #url_name = "%s_%s_%s" % (*info, self.url_list_suffix)
            url_name = self.get_base_url_name("list")
            urlpatterns += [
                path(
                    route = "", 
                    view = ListView.as_view(site=self), 
                    name = url_name
                )
            ]

        if "create" in self.allow_views:
            url_create_name = self.get_base_url_name("create")

            urlpatterns += [
                path(
                    route = f"{self.url_create_suffix}/", 
                    view = CreateView.as_view(site=self), 
                    name = url_create_name
                ),
            ]

        if "update" in self.allow_views:
            url_update_name = self.get_base_url_name("update")

            urlpatterns += [
                path(
                    route = f"{route_param}/{self.url_update_suffix}/", 
                    view = UpdateView.as_view(site=self), 
                    name = url_update_name
                ),
            ]
        
        if "detail" in self.allow_views:
            url_detail_name = self.get_base_url_name("detail")

            urlpatterns += [
                path(
                    route = f"{route_param}/{self.url_detail_suffix}/", 
                    view = DetailView.as_view(site=self), 
                    name = url_detail_name
                ),
            ]

        if "delete" in self.allow_views:
            url_delete_name = self.get_base_url_name("delete")

            urlpatterns += [
                path(
                    route = f"{route_param}/{self.url_delete_suffix}/",
                    view = DeleteView.as_view(site=self),
                    name = url_delete_name,
                ),
            ]

        urlpatterns += [
            path(
                route = f"{route_param}/{self.url_duplicate_suffix}/",
                view = DuplicateView.as_view(site=self),
                name = self.get_base_url_name("duplicate"),
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

   