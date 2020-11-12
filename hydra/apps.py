""" Hydra Apps config  """

# Django
from django.apps import AppConfig
from django.db.models.signals import post_migrate

# Utilities
from .utils import inspect_sites, get_installed_apps
from . import site


class HydraConfig(AppConfig):
    name = 'hydra'

    def ready(self):
        from . import signals
        post_migrate.connect(signals.create_actions, sender=self)
        autodiscover()

def autodiscover():
    for app in get_installed_apps():
        for cls in inspect_sites(app.name):
            site.register(cls.model, cls)
