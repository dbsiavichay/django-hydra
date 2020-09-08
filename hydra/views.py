from django.shortcuts import render
from django.urls import reverse, reverse_lazy, NoReverseMatch
from django.utils.text import slugify

from hydra.utils import (
    get_apps_from_module,
    get_models_from_app,
    get_models,
    get_apps,
)
from django.views.generic import TemplateView


class BaseView:
    """Clase base que contiene la información común de todas las subclases"""

    def get_info(self):
        """Obtiene la información de la clase"""
        info = self.model._meta.app_label, self.model._meta.model_name
        # info = self.model._meta.app_label, slugify(self.model._meta.verbose_name)
        return info

    def _get_breadcumbs(self, prefix_url_name):
        """Permite obtener los breadcumbs de auto site"""
        # Home
        base_breadcumbs = [("Inicio", "/")]
        # Prefix ulr
        if prefix_url_name:
            app_url = self._get_app_url()
            url, anything = app_url.split(self.model._meta.app_label)
            base_breadcumbs.append((prefix_url_name.capitalize(), url))
        # App url
        base_breadcumbs.append(
            (self.model._meta.app_config.verbose_name, self._get_app_url())
        )
        return base_breadcumbs

    def _get_list_breadcumbs(self, prefix_url_name):
        """Obtiene el breadcumb para List View"""
        breadcumbs = self._get_breadcumbs(prefix_url_name)
        breadcumbs.append(
            (
                self.model._meta.verbose_name_plural,
                reverse_lazy("site:%s_%s_list" % self.get_info()),
            )
        )
        return breadcumbs

    def _get_create_breadcumbs(self, prefix_url_name):
        """Obtiene el breadcumb para Create View"""
        breadcumbs = self._get_list_breadcumbs(prefix_url_name)
        breadcumbs.append(("Crear", "#"))
        return breadcumbs

    def _get_update_breadcumbs(self, prefix_url_name):
        """Obtiene el breadcumb para Update View"""
        breadcumbs = self._get_list_breadcumbs(prefix_url_name)
        breadcumbs.append(("Editar", "#"))
        return breadcumbs

    def _get_detail_breadcumbs(self, prefix_url_name):
        """Obtiene el breadcumb para Detail View"""
        breadcumbs = self._get_list_breadcumbs(prefix_url_name)
        breadcumbs.append(
            (
                str(self.object),
                reverse_lazy(
                    "site:%s_%s_detalle" % self.get_info(),
                    args=[self._get_slug_or_pk(self.object)],
                ),
            )
        )
        return breadcumbs

    def _get_delete_breadcumbs(self, prefix_url_name):
        breadcumbs = self._get_detail_breadcumbs(prefix_url_name)
        breadcumbs.append(("Eliminar", "#"))
        return breadcumbs

    def _get_app_url(self):
        """Obtiene la url de la app"""
        try:
            return reverse(f"site:{self.model._meta.app_label}")
        except NoReverseMatch as error:
            print("Error en BaseView", error)

    def _get_slug_or_pk(self, instance=None):
        if instance:
            return instance.slug if hasattr(instance, "slug") else instance.pk

    def _get_action_urls(self, instance=None):
        urls = {}
        slug_or_pk = self._get_slug_or_pk(instance=instance)
        try:
            urls.update({"add_url": reverse("site:%s_%s_crear" % self.get_info())})
        except NoReverseMatch:
            pass

        try:
            urls.update(
                {
                    "update_url": reverse(
                        "site:%s_%s_editar" % self.get_info(), args=[slug_or_pk]
                    )
                }
            )
        except NoReverseMatch:
            pass

        try:
            urls.update(
                {
                    "detail_url": reverse(
                        "site:%s_%s_detalle" % self.get_info(), args=[slug_or_pk]
                    )
                }
            )
        except NoReverseMatch:
            pass

        try:
            urls.update(
                {
                    "delete_url": reverse(
                        "site:%s_%s_eliminar" % self.get_info(), args=[slug_or_pk]
                    )
                }
            )
        except NoReverseMatch:
            pass

        return urls


class ModuleView(TemplateView):
    """Clase para definir las vistas de los módulos de aplicaciones"""

    module_name = None
    module_label = None
    template_name = None
    app_template_name = None
    icon = ""
    category = ""
    models = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({"apps": get_apps_from_module(self.module_name)})
        ctx.update({"models_permissions": get_apps(self.module_name)})
        ctx.update({"module_label": self.module_label})
        return ctx

    #
    # def has_permission(self):
    #     return False
    #     ctx = super().get_context_data(self.request.kwargs)
    #     print(ctx)
    #     user = self.request.user
    #     permissions = list()
    #     for model in ctx["models_permissions"]:
    #         permissions.append(f"{model._meta.app_label}.view_{model._meta.model_name}")
    #     return any(user.has_perm(permission) for permission in permissions)


def get_app_view(**kwargs):
    """Obtiene la vista de la aplicación"""
    from .mixins import MultiplePermissionRequiredAppMixin

    class View(MultiplePermissionRequiredAppMixin, TemplateView):
        app_route = kwargs.get("app_route")
        app_label = kwargs.get("app_label")
        template_name = kwargs.get("template_name")
        module_url = kwargs.get("module_url")
        module_label = kwargs.get("module_label")
        category = kwargs.get("category")

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx.update(
                {
                    "models_permissions": get_models(self.app_route),
                    "app_label": self.app_label,
                    "models": get_models_from_app(self.app_route),
                    "module_url": self.module_url,
                    "module_label": self.module_label,
                }
            )
            return ctx

    return View
