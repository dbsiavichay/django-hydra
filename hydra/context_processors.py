
# Models
from hydra.models import Menu


def menu(request):
    return {
        "menu_tree": build_user_menu(request.user)
    }


def build_user_menu(user):
    menu_list = list()
    if user.is_authenticated and user.is_active:
        object_list = Menu.objects.filter(parent__isnull=True)
        menu_list = get_user_menu(object_list, user)
    return menu_list


def get_user_menu(menu_list, user):
    menus = list()
    for menu in menu_list:
        obj_menu = {
            "name": menu.name,
            "url": menu.get_url(),
            "icon": menu.icon_class or "",
            "submenus": get_user_menu(menu.submenus.all(), user),
            "is_root": not menu.parent,
            "is_group": menu.is_group
        }

        if not obj_menu["submenus"] and (menu.is_group or not menu.action.has_permissions(user)):
            continue

        menus.append(obj_menu)

    return menus

