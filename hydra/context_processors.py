
# Models
from hydra.models import Menu


def menu(request):
    return {
        'menu_items': build_menu(),
    }


def build_menu():
    menu_list = Menu.objects.filter(parent__isnull=True)
    return menu_list
