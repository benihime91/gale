from ...structures import OPTIM_REGISTRY, SCHEDULER_REGISTRY
from .optimizers import *
from .lr_schedulers import *

# Register objects
# Optimizers:
opts = [RAdam, RangerGC, Ranger, RMSpropTF, RMSprop, Adam, AdamW, AdamP, SGD, SGDP]
for o in opts:
    OPTIM_REGISTRY.register(o)

# Schedulers:
scheds = [
    OneCycleLR,
    CosineAnnealingWarmRestarts,
    ReduceLROnPlateau,
    StepLR,
    MultiStepLR,
    CosineLR,
    FlatCosScheduler,
    WarmupCosineLR,
    WarmupConstantLR,
    WarmupLinearLR,
    WarmupStepLR,
]

for s in scheds:
    SCHEDULER_REGISTRY.register(s)
