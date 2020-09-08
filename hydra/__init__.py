""" Hydra init config """

from hydra.base import site, ModelSite

__all__ = ["site", "ModelSite"]

default_app_config = "hydra.apps.HydraConfig"
