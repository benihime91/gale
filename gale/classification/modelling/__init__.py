from .build import (
    build_backbone,
    build_head,
    IMAGE_CLASSIFIER_BACKBONES,
    IMAGE_CLASSIFIER_HEADS,
)

from .meta_arch import META_ARCH_REGISTRY, build_model