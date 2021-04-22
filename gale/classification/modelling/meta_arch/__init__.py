from pathlib import Path
from omegaconf import DictConfig

from ....core.utils.misc import import_all_modules
from ....core.utils.structures import META_ARCH_REGISTRY
from .image_classifier import GeneralizedImageClassifier

FILE_ROOT = Path(__file__).parent

# Register Meta Architectures
META_ARCH_REGISTRY.register(GeneralizedImageClassifier)

# @TODO: Add Vision Transformer


def build_model(cfg: DictConfig):
    """
    Build the whole model architecture, defined by ``cfg.MODEL.META_ARCHITECTURE``.
    Note that it does not load any weights from ``cfg``.
    """
    meta_arch = cfg.MODEL.META_ARCHITECTURE
    model = META_ARCH_REGISTRY.get(meta_arch)
    model = model.from_config_dict(cfg)
    return model


import_all_modules(FILE_ROOT, "gale.classification.modelling.meta_arch")