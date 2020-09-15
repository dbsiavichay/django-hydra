# Python
import inspect
from importlib import import_module

# Django
from django.conf import settings

# Models
from hydra.models import Menu

# Utilities
from .utils import get_apps_from_module
from .views import ModuleView
from .utils import get_apps


def menu(request):
    return {
        'menu_list': build_menu(),
    }


def build_menu():
    menu_list = Menu.objects.filter(parent__isnull=True)
    return menu_list
