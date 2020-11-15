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

