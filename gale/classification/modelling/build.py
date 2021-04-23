"""
Factory methods to build a ImageClassificationBackBone and ImageClassificationHead
from gale config
"""
import logging

from omegaconf import DictConfig

from ...core.nn.shape_spec import ShapeSpec
from .backbones import *
from .heads import *

_logger = logging.getLogger()

# Register objects in the registry's
IMAGE_CLASSIFIER_BACKBONES.register(TimmBackboneBase)
IMAGE_CLASSIFIER_BACKBONES.register(ResNetBackbone)


def build_backbone(cfg: DictConfig, input_shape: ShapeSpec):
    """
    Build a ImageClassificationBackbone defined by `cfg.MODEL.BACKBONE.name`.
    """
    backbone_name = cfg.MODEL.BACKBONE.name
    cls = IMAGE_CLASSIFIER_BACKBONES.get(backbone_name)
    init_args = cfg.MODEL.BACKBONE.init_args
    backbone = cls.from_config_dict(init_args, input_shape=input_shape)
    assert isinstance(backbone, ImageClassificationBackbone)
    return backbone


IMAGE_CLASSIFIER_HEADS.register(FastaiHead)
IMAGE_CLASSIFIER_HEADS.register(FullyConnectedHead)


def build_head(cfg: DictConfig, input_shape: ShapeSpec):
    """
    Build ImageClassification defined by `cfg.MODEL.HEAD.name`.
    """
    name = cfg.MODEL.HEAD.name
    cls = IMAGE_CLASSIFIER_HEADS.get(name)
    init_args = cfg.MODEL.HEAD.init_args
    head = cls.from_config_dict(init_args, input_shape=input_shape)
    assert isinstance(head, ImageClassificationHead)
    return head
