""" Hydra signals """
# Python
import sys
import importlib

# Django
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.conf import settings
from django.apps import apps

# Hydra
from hydra import site

# Models
from hydra.models import Menu

# Utils
from hydra.utils import get_attr_of_object
from hydra.shortcuts import get_actions_and_elements



""" Signal for presave instance """

@receiver(pre_save)
def prepopulate_slug(sender, instance, **kwargs):
    if not sender in site._registry:
        return

    model_site = site._registry[sender]
    model_name = sender._meta.model_name

    slug_fields = model_site.prepopulate_slug

    if slug_fields and not isinstance(slug_fields, tuple):
        raise ImproperlyConfigured("Field 'prepopulate_slug' must be a tuple")

    if not slug_fields:
        return

    if not hasattr(sender, "slug"):
        raise ImproperlyConfigured(f"Model '{model_name}' has not 'slug' field")

    for field in slug_fields:
        if not hasattr(sender, field):
            raise ImproperlyConfigured(f"Model '{model_name}' has no field'{str(field)}'")

    
    fields = (get_attr_of_object(instance, field) for field in slug_fields)
    slug = " ".join(fields)
    instance.slug = slugify(slug)


@receiver(post_save, sender=Menu)
def update_routes(sender, instance, **kwargs):

    post_save.disconnect(update_routes, sender=Menu)

    def update_route(menus):
        for menu in menus:
            update_route(menu.submenus.all())
            menu.route = str(menu)
            menu.save()

    update_route(instance.submenus.all())

    post_save.connect(update_routes, sender=Menu)


def create_actions(app_config, using, **kwargs):
    """
    Create actions for models and views.
    """
    Action = app_config.get_model("Action")

    for app in apps.get_app_configs():
        if not app.models_module:
            continue

        actions, elements, m, v = get_actions_and_elements(app, using, Action)

        if not elements:
            continue

        acts = []
        acts += [
            Action(
                type=Action.TYPE.object,
                name=name,
                app_label=app.label,
                element=element,
            )
            for (element, name) in m.items()
            if element not in actions
        ]
        acts += [
            Action(
                type=Action.TYPE.view,
                name=name,
                app_label=app.label,
                element=element,
            )
            for (element, name) in v.items()
            if element not in actions
        ]

        Action.objects.using(using).bulk_create(acts)
