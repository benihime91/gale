__all__ = [
    "GeneralizedImageClassifier",
    "build_model",
    "META_ARCH_REGISTRY",
    "VisionTransformer",
    "VisionTransformerDataClass",
]

import logging

from omegaconf import DictConfig

from ....utils.structures import META_ARCH_REGISTRY
from .common import *
from .vision_transformer import *

_logger = logging.getLogger(__name__)

# Register Meta Architectures
META_ARCH_REGISTRY.register(GeneralizedImageClassifier)
META_ARCH_REGISTRY.register(VisionTransformer)


def build_model(cfg: DictConfig):
    """
    Build the whole model architecture, defined by ``cfg.MODEL.META_ARCHITECTURE``.
    Note that it does not load any weights from ``cfg``.
    """
    meta_arch = cfg.model.meta_architecture.name
    _logger.info("Building {} from config ...".format(meta_arch))
    model = META_ARCH_REGISTRY.get(meta_arch)
    model = model.from_config_dict(cfg)
    return model
