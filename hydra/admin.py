""" Hydra model admin """

# Django
from django.contrib import admin

# Models
from hydra.models import Action, Menu

# Forms
from hydra.forms import ActionForm, MenuForm

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    model = Action
    form = ActionForm
    list_display = ("__str__", "app_label")


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    model = Menu
    form = MenuForm
    list_display = ('__str__', 'action',)