# Python
import inspect

# Django
from django.views.generic import View
from django.urls import reverse, NoReverseMatch
from django.apps import apps

def get_slug_or_pk(object):
    if object:
        return object.slug if hasattr(object, "slug") and object.slug else object.pk


def get_urls_of_site(site, object=None):
    urls = {}

    slug_or_pk = get_slug_or_pk(object)

    try:
        url_name = site.get_url_name("list")
        urls.update({"list_url": reverse(url_name)})
    except NoReverseMatch:
        print("Url not found: %s" % url_name)

    try:
        url_name = site.get_url_name("create")
        urls.update({"create_url": reverse(url_name)})
    except NoReverseMatch:
        print("Url not found: %s" % url_name)

    if not slug_or_pk:
        return urls

    try:
        url_name = site.get_url_name("update")
        urls.update({"update_url": reverse(url_name, args=[slug_or_pk])})
    except NoReverseMatch:
        print("Url not found: %s" % url_name)

    try:
        url_name = site.get_url_name("detail")
        urls.update({"detail_url": reverse(url_name, args=[slug_or_pk])})
    except NoReverseMatch:
        print("Url not found: %s" % url_name)

    try:
        url_name = site.get_url_name("delete")
        urls.update({"delete_url": reverse(url_name, args=[slug_or_pk])})
    except NoReverseMatch:
        print("Url not found: %s" % url_name)

    return urls


def get_actions_and_elements(app_config, using, Action):
    actions = {
        action.element: action
        for action in Action.objects.filter(app_label=app_config.label)
    }

    model_elements = {
        model._meta.model_name: (
            f"{app_config.verbose_name.capitalize()} | {model._meta.verbose_name.capitalize()}"
        )
        for model in app_config.get_models()
    }

    if hasattr(app_config.module, "views"):
        view_elements = {
            name: (
                f"{app_config.verbose_name.capitalize()} | {name}"
            )
            for name, candidate in inspect.getmembers(app_config.module.views, inspect.isclass)
            if issubclass(candidate, View)
        }
    else:
        view_elements = {}

    elements = {
        **model_elements,
        **view_elements
    }

    return actions, elements, model_elements, view_elements
