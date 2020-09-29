import inspect
from importlib import import_module

from django.conf import settings

from .utils import get_apps_from_module
from .views import ModuleView
from .utils import get_apps


def sidebar(request):
    return {"sidebar": build_menu(request), "menu": build_menu(request)}


def build_menu(request):
    path = settings.SETTINGS_MODULE.split(".")[0]
    try:
        mod = import_module(path + ".views")
        views = (
            cls
            for name, cls in inspect.getmembers(mod)
            if inspect.isclass(cls)
            and issubclass(cls, ModuleView)
            and not cls == ModuleView
        )

        for view in views:
            yield {
                "verbose_name": view.module_label
                if view.module_label
                else view.module_name,
                "icon": view.icon,
                "category": view.category,
                "apps": get_apps_from_module(view.module_name),
                "permissions": get_apps(view.module_name),
            }

    except ModuleNotFoundError as error:
        pass
