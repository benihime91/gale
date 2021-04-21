# from .backbones import IMAGE_CLASSIFIER_BACKBONES, ImageClassificationBackbone
# from .heads import IMAGE_CLASSIFIER_HEADS, ImageClassificationHead

# def build_backbone(cfg, input_shape=None):
#     """
#     Build a backbone from `cfg.MODEL.BACKBONE.NAME`.
#     Returns:
#         an instance of :class:`Backbone`
#     """
#     if input_shape is None:
#         input_shape = ShapeSpec(channels=len(cfg.MODEL.PIXEL_MEAN))

#     backbone_name = cfg.MODEL.BACKBONE.name
#     backbone = IMAGE_CLASSIFIER_BACKBONES.get(backbone_name)(cfg, input_shape)
#     assert isinstance(backbone, Backbone)
#     return backbone