# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05_classification.data.common.ipynb (unless otherwise specified).

__all__ = ['pil_loader', 'cv2_loader', 'denormalize', 'show_image_batch', 'DatasetDict', 'ClassificationMapper',
           'ClassificationDataset', 'FolderParser', 'PandasParser', 'CSVParser']

# Cell
import logging
import os
from collections import namedtuple
from typing import *

import albumentations as A
import cv2
import numpy as np
import pandas as pd
import torch
import torchvision.transforms as T
from fastcore.all import *
from PIL import Image
from timm.data.constants import *
from timm.data.parsers.parser import Parser
from timm.data.parsers.parser_image_folder import ParserImageFolder

_logging = logging.getLogger(__name__)

# Cell
def pil_loader(path: str) -> Image.Image:
    """
    Loads in a Image using PIL
    """
    im = Image.open(path).convert("RGB")
    return im

# Cell
def cv2_loader(path: str) -> np.ndarray:
    """
    Loads in a Image using cv2
    """
    im = cv2.imread(path)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return im

# Cell
@typedispatch
def convert_image(image: Image.Image):
    return np.array(image)

# Cell
@typedispatch
def convert_image(image: np.ndarray):
    return Image.fromarray(image)

# Cell
@typedispatch
def load_and_apply_image_transforms(path: str, transforms: A.Compose):
    image = cv2_loader(path)
    aug_image = transforms(image=image)
    return aug_image["image"]

# Cell
@typedispatch
def load_and_apply_image_transforms(path: str, transforms: T.Compose):
    image = pil_loader(path)
    aug_image = transforms(image)
    return aug_image

# Cell
@typedispatch
def apply_transforms(im: Image.Image, transform: T.Compose):
    return transform(im)

# Cell
@typedispatch
def apply_transforms(im: Image.Image, transform: A.Compose):
    image = np.array(im)
    return transform(image=image)["image"]

# Cell
def denormalize(x: torch.Tensor, mean: torch.FloatTensor, std: torch.FloatTensor):
    "Denormalize `x` with `mean` and `std`."
    return x.cpu().float() * std[..., None, None] + mean[..., None, None]

# Cell
@use_kwargs_dict(
    keep=True,
    figsize=None,
    imsize=3,
    suptitle=None,
)
def show_image_batch(
    batch: Tuple[torch.Tensor],
    n: int = 8,
    mean=IMAGENET_DEFAULT_MEAN,
    std=IMAGENET_DEFAULT_STD,
    nrows=2,
    ncols=4,
    **kwargs
):
    "Displays an image batch after applying `denormalize`"
    images, labels = batch
    images, labels = images[:n], labels[:n]
    if not isinstance(mean, torch.Tensor):
        mean = torch.Tensor(mean).float()
    if not isinstance(std, torch.Tensor):
        std = torch.Tensor(std).float()

    images = denormalize(images, mean, std)
    images = images.clip(0, 1)
    labels = [x.cpu().numpy().item() for x in labels]
    show_images(ims=images, titles=labels, nrows=nrows, ncols=ncols, **kwargs)

# Cell
class DatasetDict(namedtuple("dataset_dict", ["file_name", "target"])):
    """
    A simple structure that contains the path to the Images and
    Interger target of the Images.
    """

    def __new__(cls, file_name: str, target: int):
        return super().__new__(cls, file_name, target)

# Cell
class ClassificationMapper(DisplayedTransform):
    decodes = noop
    """
    A callable which takes in a dataset and map it into a format used by the model.
    This mapper takes in a Dict/str as input . The key "file_name" must contain the
    path to the Image to be loaded and key "target" must contain the integer target.

    The callable currently does the following:
    1. Reads in the image from `file_name`.
    2. Applies transformations to the Images
    3. Converts dataset to return `torch.Tensor` Images & `torch.long` targets

    You can also optionally pass in `xtras` these which must be a callable functions. This function
    is applied after converting the images to to tensors. Helpfull for applying trasnformations like
    RandomErasing which requires the inputs to be tensors.
    """

    def __init__(
        self,
        augmentations: Optional[Union[T.Compose, A.Compose]] = None,
        mean: Sequence[float] = IMAGENET_DEFAULT_MEAN,
        std: Sequence[float] = IMAGENET_DEFAULT_STD,
        xtras: Optional[Callable] = noop,
    ):
        """
        Arguments:
        1. `augmentations`: a list of augmentations or deterministic transforms to apply
        2. `mean`, `std`: list or tuple with #channels element, representing the per-channel mean and
        std to be used to normalize the input image. Note: These should be normalized values.
        4. `xtras`: A callable funtion applied after images are normalized and converted to tensors.
        """
        super().__init__()
        store_attr()

        # fmt: off
        self.normalize = T.Compose([
            T.ToTensor(),
            T.Normalize(torch.tensor(self.mean), torch.tensor(self.std)),
        ])
        # fmt: on

    def encodes(self, dataset_dict: DatasetDict):
        """
        For normal use-cases
        """
        # fmt: off
        image = load_and_apply_image_transforms(dataset_dict.file_name, self.augmentations)
        # fmt: on
        image = self.normalize(image)
        image = self.xtras(image)

        assert isinstance(image, torch.Tensor)

        target = dataset_dict.target
        target = torch.tensor(target, dtype=torch.long)
        return image, target

    def encodes(self, torchvision_instance: Tuple):
        """
        For torhcvision instances
        """
        image, target = torchvision_instance
        image = apply_transforms(image, self.augmentations)
        image = self.normalize(image)
        image = self.xtras(image)

        assert isinstance(image, torch.Tensor)

        target = torch.tensor(target, dtype=torch.long)
        return image, target

# Cell
class ClassificationDataset(torch.utils.data.Dataset):
    """
    Map a function over the elements returned by a parser
    """

    def __init__(self, parser: Parser, mapper: DisplayedTransform):
        """
        Arguments:

        1. `mapper`: a callable which maps the element in dataset, typically `ClassificationMapper`.
        2. `parser`: a `Parser` to load in the Images and their corresponding targets.
        """
        store_attr("parser, mapper")

    def __len__(self):
        return len(self.parser)

    def __getitem__(self, index):
        dataset_dict = self.parser[index]
        # preprocess and load the data
        return self.mapper.encodes(dataset_dict)

# Cell
class FolderParser(ParserImageFolder):
    """
    A generic parser which loads data from `root` where samples are arranged in this way:

    ```
    root/class_x/xxx.ext
    root/class_x/xxy.ext
    root/class_x/[...]/xxz.ext

    root/class_y/123.ext
    root/class_y/nsdf3.ext
    root/class_y/[...]/asd932_.ext

    ```
    """

    def __getitem__(self, index):
        path, target = self.samples[index]
        return DatasetDict(file_name=path, target=target)

# Cell
class PandasParser(Parser):
    """
    A generic parser which parser data from a pandas dataframe
    """

    def __init__(self, df: pd.DataFrame, path_column: str, label_column: str):
        """
        Arguments:

        1. `df`: a pandas dataframe
        2. `path_columne`: name of the column where the Images are stored.
        3. `label_column`: name of the column where the Image targets are stored.
        """
        self.df = df
        imgs = self.df[path_column]
        labels = self.df[label_column]
        self.samples = [(i, t) for i, t in zip(imgs, labels)]

    def __getitem__(self, index):
        path, target = self.samples[index]
        return DatasetDict(file_name=str(path), target=target)

    def __len__(self):
        return len(self.samples)

    def _filename(self, index):
        return self.samples[index][0]

    def filename(self, index):
        return self._filename(index)

    def filenames(self):
        return [self._filename(index) for index in range(len(self))]

# Cell
class CSVParser(PandasParser):
    """
    Parser for csv files. Parser first loads in csv as a pandas dataframe
    and rest functionality is same as `PandasParser`
    """

    @delegates(pd.read_csv)
    def __init__(self, path: str, path_column: str, label_column: str, **kwargs):
        """
        Arguments:

        1. `path`: path to a csv file
        2. `path_columne`: name of the column where the Images are stored.
        3. `label_column`: name of the column where the Image targets are stored.
        """
        self.df = pd.read_csv(path, **kwargs)
        imgs = self.df[path_column]
        labels = self.df[label_column]
        self.samples = [(i, t) for i, t in zip(imgs, labels)]