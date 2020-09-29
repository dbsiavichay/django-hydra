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
    list_fields = ("name", "route","content_type", "sequence")
