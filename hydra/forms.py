""" Forms for menu """
# Django
from django.forms import ModelForm

# Models
from .models import Menu

class MenuForm(ModelForm):
    class Meta:
        model = Menu
        exclude = ('route',)

    def save(self, commit=True):
        menu = super().save(commit=False)
        menu.route = str(menu)
        if commit:
            menu.save()
        return menu