# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_torch_utils.ipynb (unless otherwise specified).

__all__ = ['norm_types', 'bn_types', 'init_default', 'cond_init', 'apply_leaf', 'apply_init', 'set_bn_eval',
           'trainable_params', 'params', 'maybe_convert_to_onehot', 'worker_init_fn', 'build_discriminative_lrs']

# Cell
from functools import partial
from typing import *

import numpy as np
import torch
from fastcore.all import *
from torch import nn

# Cell
norm_types = (
    nn.BatchNorm1d,
    nn.BatchNorm2d,
    nn.BatchNorm3d,
    nn.InstanceNorm1d,
    nn.InstanceNorm2d,
    nn.InstanceNorm3d,
    nn.LayerNorm,
)

bn_types = (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)

# Cell
def init_default(m: nn.Module, func: Callable = nn.init.kaiming_normal_):
    """
    Initialize `m` weights with `func` and set `bias` to 0.
    Source: https://github.com/fastai/fastai/blob/master/fastai/torch_core.py
    """
    if func:
        if hasattr(m, "weight"):
            func(m.weight)
        if hasattr(m, "bias") and hasattr(m.bias, "data"):
            m.bias.data.fill_(0.0)
    return m

# Cell
def cond_init(m: nn.Module, func: Callable):
    """
    Apply `init_default` to `m` unless it's a batchnorm module.
    Source: https://github.com/fastai/fastai/blob/master/fastai/torch_core.py
    """
    if not isinstance(m, norm_types):
        init_default(m, func)

# Cell
def apply_leaf(m: nn.Module, f: Callable):
    """
    Apply `f` to children of `m`.
    Source: https://github.com/fastai/fastai/blob/master/fastai/torch_core.py
    """
    c = m.children()
    if isinstance(m, nn.Module):
        f(m)
    for l in c:
        apply_leaf(l, f)

# Cell
def apply_init(m: nn.Module, func: Callable = nn.init.kaiming_normal_):
    """
    Initialize all non-batchnorm layers of `m` with `func`.
    Source: https://github.com/fastai/fastai/blob/master/fastai/torch_core.py
    """
    apply_leaf(m, partial(cond_init, func=func))

# Cell
def set_bn_eval(m: nn.Module):
    """
    Recursively Set bn layers in eval mode for all recursive children of `m`.
    Source: https://github.com/fastai/fastai/blob/master/fastai/callback/training.py#L43
    """
    for l in m.children():
        if isinstance(l, bn_types):
            l.eval()
        set_bn_eval(l)

# Cell
def trainable_params(m: nn.Module):
    "Return all trainable parameters of `m`"
    return [p for p in m.parameters() if p.requires_grad]

# Cell
def params(m):
    "Return all parameters of `m`"
    return [p for p in m.parameters()]

# Cell
# fmt: off
def maybe_convert_to_onehot(target: torch.Tensor, output: torch.Tensor) -> torch.LongTensor:
    """
    This function infers whether `target` is `one_hot` encoded
    and converts it to `one_hot` encoding if necessary.

    Returns a `one_hot` encoded `torch.LongTensor` with same shape as output.

    Shape:
    - Output : $(N, C)$ where N is the mini-batch size and $C$ is the total number of classes.
    - Returns: $(N, C)$
    """
    target_shape_list = list(target.size())
    if len(target_shape_list) == 1 or (
        len(target_shape_list) == 2 and target_shape_list[1] == 1
    ):
        target = torch.nn.functional.one_hot(target, output.shape[1])
    return target
# fmt: on

# Cell
def worker_init_fn(worker_id: int):
    """
    You can set the seed for `NumPy` in the `worker_init_fn` of `DataLoader`s

    For more information see:
    https://tanelp.github.io/posts/a-bug-that-plagues-thousands-of-open-source-ml-projects/
    """
    np.random.seed(np.random.get_state()[1][0] + worker_id)

# Cell
def build_discriminative_lrs(
    param_list: List[Dict], lr_stop: float, lr_start: Optional[float] = None
):
    """
    Build a range of discriminative lrs from `lr_start` to `lr_stop`
    """
    if lr_start:
        lrs = even_mults(lr_start, lr_stop, len(param_list))
    else:
        lrs = even_mults(lr_stop / 100, lr_stop, len(param_list))

    lrs = L(lrs, use_list=False)

    if len(lrs) == 1:
        lrs = lrs * len(param_list)

    assert len(lrs) == len(
        param_list
    ), f"Trying to set {len(lrs)} values, but there are {len(param_list)} parameter groups."

    for v_, p in zip(lrs, param_list):
        p["lr"] = v_
    return param_list, list(lrs)