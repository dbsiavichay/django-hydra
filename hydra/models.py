""" Models for buid menus """

# Django
from django.db import models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

# Utilities
from .utils import get_model_info


class Menu(models.Model):
    """ Models for menu """

    parent = models.ForeignKey(
        'self',
        blank = True,
        null = True, 
        related_name='submenus',
        on_delete=models.CASCADE, 
        verbose_name='menú padre'
    )
    name = models.CharField(max_length=128, verbose_name='nombre')
    route = models.CharField(max_length=512, verbose_name='ruta')
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        blank = True,
        null = True, 
        on_delete=models.CASCADE, 
        verbose_name='modelo'
    )
    icon_class = models.CharField(
        max_length=128,
        blank=True,
        null=True, 
        verbose_name='clase css del ícono'
    )
    sequence = models.PositiveSmallIntegerField(verbose_name='secuencia')
    is_active = models.BooleanField(default=True, verbose_name='activo?')

    class Meta:
        ordering = ('route', 'sequence')

    def __str__(self):
        return f'{self.parent}/{self.name}' if self.parent else self.name

    def get_url(self):
        model_class = self.content_type.model_class() if self.content_type else self.content_type
        url = '#'
        if model_class:
            info = get_model_info(model_class)
            try:
                url = reverse('site:%s_%s_list' % info)
            except NoReverseMatch:
                pass
             
        return url

def map():
    Menu.objects.all().delete()
    configs = (app for app in apps.get_app_configs() if 'apps' in app.name)
    sequence = 1
    for app in configs:
        menu = Menu.objects.create(
            name = app.verbose_name.capitalize(),
            route = app.verbose_name,
            sequence = sequence
        )
        sequence += 1

        index = 1
        for model in app.get_models():
            submenu = Menu(
                parent = menu,
                name = model._meta.verbose_name_plural.capitalize(),
                content_type = ContentType.objects.get_for_model(model),
                sequence = index
            )

            submenu.route = str(submenu)
            submenu.save()
            index += 1

