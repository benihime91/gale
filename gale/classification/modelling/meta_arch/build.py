from omegaconf import DictConfig

from ....core.utils.structures import META_ARCH_REGISTRY
from .general import GeneralizedImageClassifier
from .vit import ViT

# Register Meta Architectures
META_ARCH_REGISTRY.register(GeneralizedImageClassifier)
META_ARCH_REGISTRY.register(ViT)


def build_model(cfg: DictConfig):
    """
    Build the whole model architecture, defined by ``cfg.MODEL.META_ARCHITECTURE``.
    Note that it does not load any weights from ``cfg``.
    """
    meta_arch = cfg.MODEL.META_ARCHITECTURE
    model = META_ARCH_REGISTRY.get(meta_arch)
    model = model.from_config_dict(cfg)
    return model
