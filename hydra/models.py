""" Models for buid menus """

# Django
from django.db import models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.text import slugify
from django.apps import apps

# Hydra
from . import site


class Action(models.Model):
    class TYPE(models.IntegerChoices):
        object = 1, "Objecto"
        view = 2, "Vista"

    APP_CHOICES = (
        (app.label, app.verbose_name.capitalize()) for app in apps.get_app_configs()
    )

    type = models.PositiveSmallIntegerField(
        choices=TYPE.choices,
        verbose_name="tipo de acción"
    )
    name = models.CharField(max_length=128, verbose_name='nombre de la acción') 
    app_label = models.CharField(
        max_length=128,
        choices=APP_CHOICES,
        verbose_name="aplicación"
    )
    element = models.CharField(
        max_length=128,
        verbose_name='elemento accionado'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "acción"
        verbose_name_plural = "acciones"
        unique_together = ("app_label", "element")
        ordering = ("name",)

    def get_model_class(self):
        if self.type != self.TYPE.object:
            return None
        try:
            model_class = apps.get_model(self.app_label, self.element)
            return model_class
        except LookupError:
            return None

    def get_view_class(self):
        if self.type != self.TYPE.view:
            return None
        try:
            app_config = apps.get_app_config(self.app_label)
            view_class = getattr(app_config.module.views, self.element)
            return view_class
        except LookupError:
            return None



class Menu(models.Model):
    """ Models for menu """

    parent = models.ForeignKey(
        'self',
        blank=True, null=True,
        related_name='submenus',
        on_delete=models.CASCADE,
        verbose_name='menú padre'
    )
    name = models.CharField(max_length=128, verbose_name='nombre')
    route = models.CharField(
        max_length=512,
        unique=True,
        verbose_name='ruta de acceso'
    )
    action = models.ForeignKey(
        Action,
        on_delete=models.CASCADE,
        verbose_name='acción'
    )
    icon_class = models.CharField(
        max_length=128,
        blank=True, null=True, 
        verbose_name='clase css del ícono'
    )
    sequence = models.PositiveSmallIntegerField(verbose_name='secuencia')
    is_active = models.BooleanField(default=True, verbose_name='activo?')

    class Meta:
        ordering = ('route', 'sequence')

    def __str__(self):
        res = f'{self.parent}/{slugify(self.name)}' if self.parent else slugify(self.name)
        return res

    def get_url(self):
        url_name = None
        if self.action.type == Action.TYPE.object:
            model_class = self.action.get_model_class()
            if model_class and model_class in site._registry:
                model_site = site._registry[model_class]
                url_name = model_site.get_url_name("list")
        else:
            url_name = f"site:{slugify(self.name)}"
        try:
            url = reverse(url_name)
            return url
        except NoReverseMatch:
            print("Not found url for %s" % url_name)

        return url_name


def map():
    Menu.objects.all().delete()

    default_action = Action.objects.get(app_label="hydra", element="ModuleView")

    apps = {}
    for model in site._registry:
        if model._meta.app_config in apps:
            apps[model._meta.app_config].append(model)
        else:
            apps[model._meta.app_config] = [model]

    sequence = 1
    for app in apps:
        menu = Menu.objects.create(
            name=app.verbose_name.capitalize(),
            action=default_action,
            route=slugify(app.verbose_name),
            sequence=sequence
        )
        sequence += 1

        index = 1
        for model in apps[app]:
            action = Action.objects.get(app_label=app.label, element=model._meta.model_name)

            submenu = Menu(
                parent=menu,
                name=model._meta.verbose_name_plural.capitalize(),
                action=action,
                sequence=index
            )

            submenu.route = str(submenu)
            submenu.save()
            index += 1
