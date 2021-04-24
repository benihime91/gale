__all__ = ["get_config", "get_class_path"]

from fastcore.all import delegates
from omegaconf import DictConfig

from hydra.experimental import compose, initialize_config_module


@delegates(compose)
def get_config(config_name="classification", **kwargs) -> DictConfig:
    """
    Get a copy of the default config.
    """
    with initialize_config_module("gale.hydra"):
        cfg = compose(config_name, **kwargs)
    return cfg.copy()


def get_class_path(cls) -> str:
    """
    Utility for building the class path
    """
    return f"{cls.__module__}.{cls.__name__}"
