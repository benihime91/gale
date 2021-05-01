__all__ = ['ACTIVATION_REGISTRY', 'GELU', 'LeakyReLU', 'ReLU', 'Sigmoid', 'SiLU', 'Softmax', 'Tanh', 'Mish']

from timm.models.layers import Mish
from torch.nn import GELU, LeakyReLU, ReLU, Sigmoid, SiLU, Softmax, Tanh

from .structures import ACTIVATION_REGISTRY

# Register Common Activation Functions
ACTIVATION_REGISTRY.register(Mish)
ACTIVATION_REGISTRY.register(GELU)
ACTIVATION_REGISTRY.register(LeakyReLU)
ACTIVATION_REGISTRY.register(ReLU)
ACTIVATION_REGISTRY.register(Sigmoid)
ACTIVATION_REGISTRY.register(SiLU)
ACTIVATION_REGISTRY.register(Softmax)
ACTIVATION_REGISTRY.register(Tanh)
