# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_core.classes.ipynb (unless otherwise specified).

__all__ = ['Configurable', 'GaleModule', 'OptimSchedBuilder', 'GaleTask']

# Cell
import copy
import logging
import math
from abc import ABC, ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import *

import hydra
import pytorch_lightning as pl
import torch
import torchmetrics
from fastcore.all import L, noop, patch
from omegaconf import DictConfig, OmegaConf
from torch.nn import Module

from .nn.optim import OPTIM_REGISTRY, SCHEDULER_REGISTRY
from .nn.utils import params, trainable_params
from .utils.logger import log_main_process

_logger = logging.getLogger(__name__)

# Cell
class Configurable(ABC):
    """
    Helper Class to instantiate obj from config
    """

    @classmethod
    def from_config_dict(cls, config: DictConfig, **kwargs):
        """
        Instantiates object using `DictConfig-based` configuration. You can optionally
        pass in extra `kwargs`
        """
        # Resolve the config dict
        if isinstance(config, DictConfig):
            config = OmegaConf.to_container(config, resolve=True)
            config = OmegaConf.create(config)

        if "_target_" in config:
            # regular hydra-based instantiation
            instance = hydra.utils.instantiate(config=config, **kwargs)
        else:
            # instantiate directly using kwargs
            try:
                instance = cls(cfg=config, **kwargs)
            except:
                cfg = OmegaConf.to_container(config, resolve=True)
                instance = cls(**config, **kwargs)

        if not hasattr(instance, "_cfg"):
            instance._cfg = config
        return instance

    def to_config_dict(self) -> DictConfig:
        # fmt: off
        """Returns object's configuration to config dictionary"""
        if hasattr(self, "_cfg") and self._cfg is not None and isinstance(self._cfg, DictConfig):
            # Resolve the config dict
            config = OmegaConf.to_container(self._cfg, resolve=True)
            config = OmegaConf.create(config)
            OmegaConf.set_struct(config, True)
            self._cfg = config

            return self._cfg
        else:
            raise NotImplementedError("to_config_dict() can currently only return object._cfg but current object does not have it.")
        # fmt: on

# Cell
class GaleModule(Module, Configurable, metaclass=ABCMeta):
    """
    Abstract class offering interface which should be implemented by all `Backbones`,
    `Heads` and `Meta Archs` in gale.
    """

    @abstractmethod
    def forward(self) -> Any:
        """
        The main logic for the model lives here. Can return either features, logits
        or loss.
        """
        raise NotImplementedError

    @abstractmethod
    def build_param_dicts(self) -> Union[Iterable, List[Dict], Dict, List]:
        """
        Should return the iterable of parameters to optimize or dicts defining parameter groups
        for the Module.
        """
        raise NotImplementedError

    @property
    def param_lists(self):
        "Returns the list of paramters in the module"
        return [p for p in self.parameters()]

    def all_params(self, n=slice(None), with_grad=False):
        "List of `param_groups` upto n"
        res = L(p for p in self.param_lists[n])
        # fmt: off
        return L(o for o in res if hasattr(o, "grad") and o.grad is not None) if with_grad else res
        # fmt: on

    def _set_require_grad(self, rg, p):
        p.requires_grad_(rg)

    def unfreeze(self) -> None:
        """
        Unfreeze all parameters for training.
        """
        for param in self.parameters():
            param.requires_grad = True

        self.train()

    def freeze(self) -> None:
        """
        Freeze all params for inference & set model to eval
        """
        for param in self.parameters():
            param.requires_grad = False
        self.eval()

    def freeze_to(self, n) -> None:
        "Freeze parameter groups up to `n`"
        self.frozen_idx = n if n >= 0 else len(self.param_lists) + n
        if self.frozen_idx >= len(self.param_lists):
            # fmt: off
            _logger.warning(f"Freezing {self.frozen_idx} groups; model has {len(self.param_lists)}; whole model is frozen.")
            # fmt: on

        for o in self.all_params(slice(n, None)):
            self._set_require_grad(True, o)

        for o in self.all_params(slice(None, n)):
            self._set_require_grad(False, o)

    @contextmanager
    def as_frozen(self):
        """
        Context manager which temporarily freezes a module, yields control
        and finally unfreezes the module.
        """
        self.freeze()

        try:
            yield
        finally:
            self.unfreeze()

# Cell
class OptimSchedBuilder:
    """
    Interface that constructs an Optimizer and Scheduler a from config.
    """

    _train_dl: Callable
    _trainer: pl.Trainer
    optimization_cfg: DictConfig

# Cell
@patch
def prepare_optimization_config(self: OptimSchedBuilder, config: DictConfig):
    """
    Prepares `OptimizationConfig` config and adds some interval
    values and infers values like max_steps, max_epochs, etc.

    This method also fills in the values for `max_iters` & `epochs`, `steps_per_epoch`
    which are required by some of the LearningRate Schedulers.
    """
    opt_config = copy.deepcopy(config)
    self.optimization_cfg = opt_config

    self.optimization_cfg["steps_per_epoch"] = len(self._train_dl)

    if self._trainer.max_epochs is None and self._trainer.max_steps is None:
        msg = "Either one of max_epochs or max_epochs must be provided in Trainer"
        log_main_process(_logger, logging.ERROR, msg)
        raise ValueError

    # compute effective num training steps
    # fmt: off
    if isinstance(self._trainer.limit_train_batches, int) and self._trainer.limit_train_batches != 0:
    # fmt: on
        dataset_size = self.trainer.limit_train_batches

    elif isinstance(self._trainer.limit_train_batches, float):
        # limit_train_batches is a percentage of batches
        dataset_size = len(self._train_dl)
        dataset_size = int(dataset_size * self._trainer.limit_train_batches)

    else:
        dataset_size = len(self._train_dl)

    num_devices = max(1, self._trainer.num_gpus, self._trainer.num_processes)

    if self._trainer.tpu_cores:
        num_devices = max(num_devices, self._trainer.tpu_cores)

    effective_batch_size = self._trainer.accumulate_grad_batches * num_devices
    max_steps = (dataset_size // effective_batch_size) * self._trainer.max_epochs

    if self._trainer.max_steps is None:
        self.optimization_cfg["max_epochs"] = self._trainer.max_epochs
        self.optimization_cfg["max_steps"] = max_steps

    else:
        epochs = self._trainer.max_steps * len(self._train_dl)
        self.optimization_cfg["max_steps"] = self._trainer.max_steps
        self.optimization_cfg["max_epochs"] = epochs

    # covert config to Dictionary
    # fmt: off
    sched_config = OmegaConf.to_container(self.optimization_cfg.scheduler.init_args, resolve=True)

    max_steps = self.optimization_cfg["max_steps"]
    max_epochs = self.optimization_cfg["max_epochs"]
    steps = self.optimization_cfg["steps_per_epoch"]

    # populate values in learning rate schedulers
    if "max_iters" in sched_config:
        if sched_config["max_iters"] == -1:
            OmegaConf.update(self.optimization_cfg, "scheduler.init_args.max_iters", max_steps)
            msg = f"Set the value of 'max_iters' to be {max_steps}."
            log_main_process(_logger, logging.DEBUG, msg)

    if "epochs" in sched_config:
        if sched_config["epochs"] == -1:
            OmegaConf.update(self.optimization_cfg, "scheduler.init_args.epochs", max_epochs)
            msg = f"Set the value of 'epochs' to be {max_epochs}."
            log_main_process(_logger, logging.DEBUG, msg)

    if "steps_per_epoch" in sched_config:
        if sched_config["steps_per_epoch"] is None:
            OmegaConf.update(self.optimization_cfg, "scheduler.init_args.steps_per_epoch", steps)
            msg = f"Set the value of 'steps_per_epoch' to be {steps}."
            log_main_process(_logger, logging.DEBUG, msg)
    # fmt: on

# Cell
@patch
def build_optimizer(self: OptimSchedBuilder, params: Any) -> torch.optim.Optimizer:
    """
    Builds a single optimizer from `OptimizationConfig`. `params` are the parameter
    dict with the weights for the optimizer to optimizer.

    Note this method must be called after `prepare_optimization_config()`
    """
    if not isinstance(self.optimization_cfg, DictConfig):
        msg = "optimization_cfg not found, did you call `prepare_optimization_config`."
        log_main_process(_logger, logging.WARNING, msg)
        raise NameError
    else:
        if self.optimization_cfg.optimizer.name is None:
            msg = "Optimizer is None, so no optimizer will be created."
            log_main_process(_logger, logging.WARNING, msg)
            opt = None
        else:
            opt = self.optimization_cfg.optimizer
            opt = OPTIM_REGISTRY.get(opt.name)(params=params, **opt.init_args)
            msg = f"Built optimizer, {opt.__class__.__name__} with {len(opt.param_groups)} param group(s)."
            log_main_process(_logger, logging.DEBUG, msg)
        return opt

# Cell
@patch
def build_lr_scheduler(
    self: OptimSchedBuilder, optimizer: torch.optim.Optimizer
) -> Any:
    """
    Builds a LearningRate scheduler from `OptimizationConfig`. Returns an LRScheduler dict
    that is required by PyTorch Lightning for LRSchedulers.
    Note this method must be called after `prepare_optimization_config()`
    """
    if not isinstance(self.optimization_cfg, DictConfig):
        msg = "optimization_cfg not found, did you call `prepare_optimization_config`."
        log_main_process(_logger, logging.WARNING, msg)
        raise NameError
    else:
        if self.optimization_cfg.scheduler.name is None:
            msg = "scheduler is None, so no scheduler will be created."
            log_main_process(_logger, logging.WARNING, msg)
            sched = None
        else:
            _c = self.optimization_cfg.scheduler.init_args
            _temp = OmegaConf.to_container(_c, resolve=True)
            kwds = {}

            # if a key value is ListConfig then we convert it to simple list
            for key, value in _temp.items():
                if isinstance(value, list):
                    kwds[key] = list(value)
                else:
                    kwds[key] = value

            instance = SCHEDULER_REGISTRY.get(self.optimization_cfg.scheduler.name)
            sch = instance(optimizer=optimizer, **kwds)

            # convert the lr_scheduler to pytorch-lightning LRScheduler dictionary format
            msg = f"LRScheduler : {sch.__class__.__name__}."
            log_main_process(_logger, logging.DEBUG, msg)
            sched = {
                "scheduler": sch,
                "interval": self.optimization_cfg.scheduler.interval,
                "monitor": self.optimization_cfg.scheduler.monitor,
            }
            return sched

# Cell
class GaleTask(pl.LightningModule, OptimSchedBuilder, metaclass=ABCMeta):
    """
    Interface for Pytorch-lightning based Gale modules
    """

    def __init__(
        self,
        cfg: DictConfig,
        trainer: Optional[pl.Trainer] = None,
        metrics: Union[torchmetrics.Metric, Mapping, Sequence, None] = None,
    ):
        """
        Base class from which all PyTorch Lightning Tasks in Gale should inherit.

        Arguments:
        1. `cfg` `(DictConfig)`:  configuration object. cfg object should be inherited from `BaseGaleConfig`.
        2. `trainer` `(Optional, pl.Trainer)`: Pytorch Lightning Trainer instance
        3. `metrics` `(Optional)`: Metrics to compute for training and evaluation.
        """
        super().__init__()
        self._cfg = OmegaConf.structured(cfg)

        self.save_hyperparameters(self._cfg)
        self._train_dl = noop
        self._validation_dl = noop
        self._test_dl = noop
        self._optimizer = noop
        self._scheduler = noop
        self._trainer = trainer
        self.metrics = metrics

    def train_dataloader(self) -> torch.utils.data.DataLoader:
        "Returns the Dataloader used for Training"
        if self._train_dl is not None and self._train_dl is not noop:
            return self._train_dl

    def val_dataloader(self) -> Any:
        "Returns the List of Dataloaders or Dataloader used for Validation"
        if self._validation_dl is not None and self._validation_dl is not noop:
            return self._validation_dl

    def test_dataloader(self) -> Any:
        "Returns the List of Dataloaders or Dataloader used for Testing"
        if self._test_dl is not None and self._test_dl is not noop:
            return self._test_dl

    @abstractmethod
    def forward(self, x: torch.Tensor):
        """
        The Forward method for LightningModule, users should modify this method.
        """
        raise NotImplementedError

    @abstractmethod
    def setup_training_data(self, train_data_config: Union[DictConfig, Dict]):
        """
        Setups data loader to be used in training

        Arguments:
        1. `train_data_config`: training data loader parameters.
        """
        raise NotImplementedError

    @abstractmethod
    def setup_validation_data(self, val_data_config: Union[DictConfig, Dict]):
        """
        Setups data loader to be used in validation

        Arguments:
        1. `val_data_config`: validation data loader parameters.
        """
        raise NotImplementedError

    def setup_test_data(
        self, test_data_config: Optional[Union[DictConfig, Dict]] = None
    ):
        """
        (Optionally) Setups data loader to be used in test

        Arguments:
        1. `test_data_config`: test data loader parameters.
        """
        raise NotImplementedError

    @property
    def param_dicts(self) -> Union[Iterator, List[Dict]]:
        """
        Property that returns the param dicts for optimization.
        Override for custom training behaviour. Currently returns all the trainable paramters.
        """
        return L(self).map(trainable_params)

    def shared_step(self, batch: Any, batch_idx: int, stage: str) -> Any:
        """
        The common training/validation/test step. Override for custom behavior. This step
        is shared between training/validation/test step. For training/validation/test steps
        `stage` is train/val/test respectively. You training logic should go here avoid directly overriding
        training/validation/test step methods.
        """
        raise NotImplementedError

    def training_step(self, batch: Any, batch_idx: int) -> Any:
        """
        The training step of the LightningModule. For common use cases you need
        not need to override this method. See `GaleTask.shared_step()`
        """
        return self.shared_step(batch, batch_idx, stage="train")

    def validation_step(self, batch: Any, batch_idx: int) -> None:
        """
        The validation step of the LightningModule. For common use cases you need
        not need to override this method. See `GaleTask.shared_step()`
        """
        return self.shared_step(batch, batch_idx, stage="val")

    def test_step(self, batch: Any, batch_idx: int) -> None:
        """
        The test step of the LightningModule. For common use cases you need
        not need to override this method. See `GaleTask.shared_step()`
        """
        return self.shared_step(batch, batch_idx, stage="test")

    def setup_optimization(self, optim_config: DictConfig = None):
        """
        Prepares an optimizer from a string name and its optional config parameters.

        Args:
        1. `optim_config`: A `dictionary`/`DictConfig` or instance of `OptimizationConfig`.
        """
        # If config was not explicitly passed to us
        if optim_config is None:
            # See if internal config has `optim` namespace
            if self._cfg is not None and hasattr(self._cfg, "optimization"):
                optim_config = self._cfg.optimization

        # If config is still None, or internal config has no Optim, return without instantiation
        if optim_config is None:
            msg = "No optimizer config provided, therefore no optimizer was created"
            log_main_process(_logger, logging.WARNING, msg)
            return

        else:
            # Preserve the configuration
            if not isinstance(optim_config, DictConfig):
                optim_config = OmegaConf.create(optim_config)

            # prepare the optimization config
            self.prepare_optimization_config(optim_config)

            # Setup optimizer and scheduler
            self._optimizer = self.build_optimizer(self.param_dicts)
            self._scheduler = self.build_lr_scheduler(self._optimizer)

    def configure_optimizers(self):
        """
        Choose what optimizers and learning-rate schedulers to use in your optimization.
        See https://pytorch-lightning.readthedocs.io/en/latest/common/optimizers.html
        """
        # if self.setup_optimization() has been called manually no
        # need to call again
        if self._optimizer is noop and self._scheduler is noop:
            self.setup_optimization()

        if self._scheduler is None:
            return self._optimizer
        else:
            return [self._optimizer], [self._scheduler]