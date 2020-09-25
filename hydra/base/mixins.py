# Django
from django.urls import reverse, reverse_lazy, NoReverseMatch


# Utils
from hydra.utils import import_class

class BreadcrumbMixin:
    """Clase base que contiene la información común de todas las subclases"""

    def get_base(self, menu):
        base = [(menu.name, f"/{menu.route}/")]
        if menu.parent:
            base =  self.get_base(menu.parent) + base
        return base


    def get_base_breadcrumbs(self):
        base_breadcrumbs = [(self.site.get_breadcrumb_text("home"), "/")]
        Menu = import_class("hydra.models", "Menu")
        if not Menu or not self.site.routes: return base_breadcrumbs
        menu = Menu.objects.get(route=self.site.routes[0])
        base_breadcrumbs.extend(self.get_base(menu))
        return base_breadcrumbs

    def get_create_breadcrumbs(self):
        """Obtiene el breadcumb para Create View"""
        breadcrumbs = self.get_base_breadcrumbs()
        breadcrumbs.append((self.site.get_breadcrumb_text("create"), "#"))
        return breadcrumbs

    def get_update_breadcrumbs(self):
        """Obtiene el breadcumb para Update View"""
        breadcrumbs = self.get_base_breadcrumbs()
        breadcrumbs.append((self.site.get_breadcrumb_text("update"), "#"))
        return breadcrumbs

    def get_detail_breadcrumbs(self):
        """Obtiene el breadcumb para Detail View"""
        url_name = self.site.get_url_name("detail")
        breadcrumbs = self.get_base_breadcrumbs()
        breadcrumbs.append(
            (
                self.site.get_breadcrumb_text("detail") or str(self.object),
                reverse_lazy(url_name, args=[self._get_slug_or_pk(self.object)],),
            )
        )
        return breadcrumbs

    def _get_delete_breadcrumbs(self):
        breadcrumbs = self.get_detail_breadcrumbs()
        breadcrumbs.append((self.site.get_breadcrumb_text("delete"), "#"))
        return breadcrumbs

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
            url_name = self.site.get_url_name("create")
            urls.update({"add_url": reverse(url_name)})
        except NoReverseMatch:
            print("Url not found: %s" % url_name)

        try:
            url_name = self.site.get_url_name("update")
            urls.update({"update_url": reverse(url_name, args=[slug_or_pk])})
        except NoReverseMatch:
            print("Url not found: %s" % url_name)

        try:
            url_name = self.site.get_url_name("detail")
            urls.update({"detail_url": reverse(url_name, args=[slug_or_pk])})
        except NoReverseMatch:
            print("Url not found: %s" % url_name)

        try:
            url_name = self.site.get_url_name("delete")
            urls.update({"delete_url": reverse(url_name, args=[slug_or_pk])})
        except NoReverseMatch:
            print("Url not found: %s" % url_name)

        return urls
