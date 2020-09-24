#Python
import inspect
import json
from importlib import import_module

# Django
from django.core.exceptions import FieldDoesNotExist
from django.forms.utils import pretty_name
from django.conf import settings
from django.apps import apps as djangoapps
from django.urls import reverse_lazy, reverse, NoReverseMatch
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS


def inspect_sites(app):
    from . import ModelSite
    results = inspect_clases(f"{app}.sites", ModelSite)
    return (cls for cls in results if cls.model is not None)


def inspect_clases(module_name, parent_class):
    results = ()
    try:
        module = import_module(module_name)
        results = (
            cls
            for name, cls in inspect.getmembers(module)
            if inspect.isclass(cls)
            and issubclass(cls, parent_class)
            and not cls == parent_class
        )
    except ModuleNotFoundError as error:
        print(error)
        pass
    return results


def get_installed_apps():
    apps = (app for app in djangoapps.get_app_configs())
    return apps

"""

def get_apps_from_module(module_name):
    apps = (app for app in get_installed_apps() if module_name in app.name)

    for app in apps:
        try:
            module_url = reverse(f"site:{app.label}")
        except NoReverseMatch as error:
            print("Error en get_apps_from_module", error)

        yield {
            "name": app.verbose_name,
            "url": module_url,
            "models": get_models_from_app(app.name),
            "permissions": get_models(app.name),
        }


def get_models_from_app(app_name):
    sites = inspect_sites(app_name)
    for site in sites:
        info = site.get_info()
        try:
            create_url = reverse("site:%s_%s_crear" % info)
        except NoReverseMatch:
            create_url = None
        if site.build_in_menu:
            yield {
                "name": site.model._meta.verbose_name_plural,
                "list_url": reverse_lazy("site:%s_%s_list" % info),
                "create_url": create_url,
                "icon": site.icon if hasattr(site, "icon") else "",
                "category": site.category if hasattr(site, "category") else "",
                "permissions": site.model,
            }


def get_project_path():
    path = settings.SETTINGS_MODULE.split(".")[0]
    return path


def get_models(app_name):
    sites = inspect_sites(app_name)
    modelos = list()
    for site in sites:
        modelos.append(site.model)
    return modelos


def get_apps(module_name):
    apps = (app for app in get_installed_apps() if module_name in app.name)
    modelos = list()
    for app in apps:
        modelos = modelos + get_models(app.name)
    return modelos


def get_modules():

    path = settings.SETTINGS_MODULE.split(".")[0]
    try:
        from .views import ModuleView

        mod = import_module(path + ".views")
        views = (
            cls
            for name, cls in inspect.getmembers(mod)
            if inspect.isclass(cls)
            and issubclass(cls, ModuleView)
            and not cls == ModuleView
        )
        modules = []

        for view in views:
            modules.append(
                {"module": view.module_name, "apps": get_apps(view.module_name)}
            )

    except ModuleNotFoundError as error:
        pass
    return modules


def get_model(app_name):
    sites = inspect_sites(app_name)
    modelos = list()
    for site in sites:
        modelos.append(site.model)
    return modelos
"""

def get_field_label_of_model(model, field):
    names = field.split(".")
    name = names.pop(0)

    try:
        name, verbose_name = name.split(":")
        return pretty_name(verbose_name)
    except ValueError:
        pass

    if not hasattr(model, name):
        try:
            str_model = f"<{model._meta.model_name}>"
        except:
            str_model = str(model)
        raise AttributeError(f"No existe le atributo <{name}> para {str_model}.")

    if len(names):
        if hasattr(model, "_meta"):
            return get_field_label_of_model(
                model._meta.get_field(name).related_model, ".".join(names)
            )
        else:
            attr = getattr(model, name)
            return get_field_label_of_model(
                attr() if callable(attr) else attr, ".".join(names)
            )
    try:
        field = model._meta.get_field(name)
        label = field.verbose_name if hasattr(field, "verbose_name") else name
    except FieldDoesNotExist:
        label = str(model._meta.verbose_name) if name == "__str__" else name

    return pretty_name(label)


def get_attribute_of_instance(instance, field):
    names = field.split(".")
    name = names.pop(0)
    name = name.split(":")[0]

    if not hasattr(instance, name):
        raise AttributeError(f"No existe le atributo <{name}> para {str(instance)}.")

    if len(names):
        return get_attribute_of_instance(getattr(instance, name), ".".join(names))

    try:
        field = instance._meta.get_field(name)
        if hasattr(field, "choices") and field.choices:
            name = f"get_{name}_display"
    except FieldDoesNotExist:
        pass

    attr = getattr(instance, name)
    return attr() if callable(attr) else attr


def get_model_info(model_class):
    """Obtiene la información de la clase"""
    info = model_class._meta.app_label, model_class._meta.model_name
    # info = self.model._meta.app_label, slugify(self.model._meta.verbose_name)
    return info

def import_class(module_name, class_name):
    cls = None
    try:
        module = import_module(module_name)
        members = inspect.getmembers(module)
        for name, klass in members:
            if name == class_name:
                cls = klass
                break
    except ModuleNotFoundError as error:
        print("Not found %s" % module_name)
    return cls

def check_migrations(db_alias):
    pass
