__all__ = ["ShapeSpec"]

from collections import namedtuple


class ShapeSpec(namedtuple("_ShapeSpec", ["channels", "height", "width"])):
    """
    A simple structure that contains basic shape specification about a tensor.
    It is often used as the auxiliary inputs/outputs of models,
    to complement the lack of shape inference ability among pytorch modules.
    From :
    https://github.com/facebookresearch/detectron2/blob/194e015a7911ef239b1339a2a0201b77cb7d7d6b/detectron2/layers/shape_spec.py#L6
    Attributes:
        channels:
        height:
        width:
    """

    def __new__(cls, channels=None, height=None, width=None):
        return super().__new__(cls, channels, height, width)