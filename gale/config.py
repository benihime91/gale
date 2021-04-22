# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_core.config.ipynb (unless otherwise specified).

__all__ = ['get_config', 'get_class_path']

# Cell
from dataclasses import dataclass, field
from typing import *

from fastcore.all import delegates
from hydra.experimental import compose, initialize_config_module
from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf

# Cell
@delegates(compose)
def get_config(config_name="classification", **kwargs):
    """
    Get a copy of the default config.
    """
    with initialize_config_module("gale.hydra"):
        cfg = compose(config_name, **kwargs)
        # cfg = OmegaConf.set_struct(cfg, True)
    return cfg.copy()

# Cell
def get_class_path(cls):
    """
    Utility for building the class path
    """
    return f"{cls.__module__}.{cls.__name__}"