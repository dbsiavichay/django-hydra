""" Models for buid menus """

# Django
from django.db import models
from django.urls import reverse_lazy

# Utilities

from .utils import get_model_info


class Menu(models.Model):
    """ Models for menú """

    parent = models.ForeignKey(
        'self',
        blank = True,
        null = True, 
        related_name='submenus',
        on_delete=models.CASCADE, 
        verbose_name='menú padre'
    )
    name = models.CharField(max_length=128, verbose_name='nombre')
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
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='fecha de creación')
    created_user = models.ForeignKey(
        'authentication.User', 
        on_delete = models.PROTECT,
        related_name = 'created_menus', 
        verbose_name = 'creado por'
    )
    modified_date = models.DateTimeField(auto_now=True, verbose_name='última fecha de modificación')
    modified_user = models.ForeignKey(
        'authentication.User', 
        on_delete=models.PROTECT, 
        related_name = 'updated_menus',
        verbose_name='modificado por'
    )
    sequence = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True, verbose_name='activo?')

    def __str__(self):
        return f'{self.parent}/{self.name}' if self.parent else self.name

    def get_url(self):
        model_class = self.content_type.model_class() if self.content_type else self.content_type
        url = '#'
        if model_class:
            info = get_model_info(model_class)
            url = reverse_lazy('site:%s_%s_list' % info)
        return url
