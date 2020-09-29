""" Hydra Apps config  """

# Django
from django.apps import AppConfig

# Utilities
from .utils import inspect_sites, get_installed_apps
from . import site


class HydraConfig(AppConfig):
    name = 'hydra'

    def ready(self):
        super().ready()
        from . import signals
        autodiscover()

def autodiscover():
    for app in get_installed_apps():
        for cls in inspect_sites(app.name):
            site.register(cls.model, cls)
