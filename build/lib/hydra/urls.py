# Django
from django.urls import path
from django.utils.text import slugify

# Views
from .views import ModuleView

#Utils
from .utils import import_class

def get_module_urls():
    urlspatterns = []
    Menu = import_class("hydra.models", "Menu")
    if Menu is None:
        print("Not found Menu")
        return urlspatterns
    
    try:
        menus = Menu.objects.filter(content_type__isnull=True)
        
        for menu in menus:
            urlspatterns.append(
                path(
                    route = "%s/" % menu.route,
                    view = ModuleView.as_view(),
                    name = slugify(menu.name)
                )
            ) 
    except:
        pass
    return urlspatterns

