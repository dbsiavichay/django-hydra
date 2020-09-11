""" Hydra model admin """

# Django
from django.contrib import admin

# Models
from hydra.models import Menu

# Forms
from hydra.forms import MenuForm

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    model = Menu
    form = MenuForm
    list_display = ('__str__', 'content_type',)