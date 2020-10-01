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

# Hydra
from hydra import site

# Models
from hydra.models import Menu

# Utils
from hydra.utils import get_attr_of_object



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
    post_save.disconnect(update_routes)
    def update_route(menus):
        if not menus: return
        for menu in menus:
            update_route(menu.submenus.all())
            menu.route = str(menu)
            menu.save()

    update_route(instance.submenus.all())
    post_save.connect(update_routes)