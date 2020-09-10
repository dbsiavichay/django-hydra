""" Hydra model admin """

# Django
from django.contrib import admin

# Models
from hydra.models import Menu

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    model = Menu
    list_display = ('__str__', 'content_type',)