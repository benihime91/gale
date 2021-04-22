from omegaconf import DictConfig

from ...core.nn.shape_spec import ShapeSpec
from .backbones import IMAGE_CLASSIFIER_BACKBONES, ImageClassificationBackbone
from .heads import IMAGE_CLASSIFIER_HEADS, ImageClassificationHead


def build_backbone(cfg: DictConfig, input_shape: ShapeSpec = None):
    """
    Build a ImageClassificationBackbone defined by `cfg.MODEL.BACKBONE.name`.
    """
    if input_shape is None:
        input_shape = ShapeSpec(channels=len(cfg.MODEL.PIXEL_MEAN))

    backbone_name = cfg.MODEL.BACKBONE.name
    cls = IMAGE_CLASSIFIER_BACKBONES.get(backbone_name)
    init_args = cfg.MODEL.BACKBONE.init_args
    backbone = cls.from_config_dict(init_args, input_shape=input_shape)
    assert isinstance(backbone, ImageClassificationBackbone)
    return backbone


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
