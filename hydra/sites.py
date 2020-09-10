""" Sites for menus """

# Models
from .models import Menu

# Model Site
from hydra import ModelSite


class AccountSite(ModelSite):
    """Site for menu model"""

    model = Menu
