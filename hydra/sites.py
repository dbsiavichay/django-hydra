""" Sites for menus """

# Models
from .models import Menu

# Forms
from .forms import MenuForm

# Model Site
from hydra import ModelSite

class MenuSite(ModelSite):
    """Site for menu model"""

    model = Menu
    form_class = MenuForm
    list_display = ('__str__', 'content_type', 'icon_class', 'sequence')
