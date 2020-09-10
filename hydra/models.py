""" Models for buid menus """

# Django
from django.db import models


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
    is_active = models.BooleanField(default=True, verbose_name='activo?')

    def __str__(self):
        return f"{self.parent}/{self.name}" if self.parent else self.name
