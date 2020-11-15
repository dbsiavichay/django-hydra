""" Hydra Apps config  """

# Django
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class HydraConfig(AppConfig):
    name = 'hydra'

    def ready(self):
        from . import signals
        #post_migrate.connect(signals.create_actions, sender=self)
        self.module.autodiscover()
