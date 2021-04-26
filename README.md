# PyTorch Gale



![CI](https://github.com/benihime91/gale/workflows/CI/badge.svg)
![Docs](https://img.shields.io/website?down_message=down&label=docs&up_color=green&up_message=passing&url=https%3A%2F%2Fbenihime91.github.io%2Fgale%2F)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


**⚡️Flexible interface for solving computer vision tasks leveraging [Pytorch Lightning](https://github.com/PyTorchLightning/pytorch-lightning), [PyTorch Image Models](https://github.com/rwightman/pytorch-image-models) , and [Hydra](https://github.com/facebookresearch/hydra). ⚡️**

---

![PyTorch](https://img.shields.io/badge/-PyTorch-ee4c2c?style=for-the-badge&logo=pytorch&logoColor=white)
![Lightning](https://img.shields.io/badge/-Lightning-792ee5?style=for-the-badge)
![Config: hydra](https://img.shields.io/badge/config-hydra-89b8cd?style=for-the-badge)
![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg?style=for-the-badge)

## Requirements
1. Linux or macOS with Python ≥ 3.6

2. PyTorch ≥ 1.7.0 and [torchvision](https://github.com/pytorch/vision/) that matches the PyTorch installation. Install them together at [pytorch.org](https://pytorch.org/) to make sure of this.

## Installation

You can install PyTorch Gale from source

```bash
git clone https://github.com/benihime91/gale
cd gale
pip install .
```

If you plan to develop PyTorch Gale yourself you can use an editable install 
```bash
git clone https://github.com/benihime91/gale
pip install -e "gale[dev]"
```

## Introduction
PyTorch Gale tasks allow you to train models using `PyTorch Image Models` models, use Hydra to hotswap models, optimizers or schedulers and leverage all the advances features that Lightning has to offer, including custom Callbacks, Loggers, Accelerators and high performance scaling with minimal changes.

This project was started as a way to collect interesting techniques dotted throughout Kaggle competitions and varous deep learning forums which have been usefull in training accuracte deep learning models for Computer Vision Tasks. 

Currently PyTorch Gale only supports Image Classification. The final goal is to be able to support both Object Detection and Image Segmentation hopefully.

PyTorch Gale is beta software. The project is under active development and our APIs are subject to change in future releases. The current API of PyTorch Gale is highly inspired from [Detectron 2](https://github.com/facebookresearch/detectron2).

PyTorch Gale comes with all the goodness that comes in PyTorch Lightning. Using the training script `train.py` [WIP] you can override any config parameter from command line. The same code can be trained on CPU, GPU even TPUs. Hydra configuration makes it easy to keep track of training hyperparameters enabling you to interate over different parameters without changing the code, just make minor changes to the config. Some examples configs are given in `references` [WIP].

PyTorch Gale also comes with a few usefull tricks to streamline you trainings and also has extensive callbacks for PyTorch Lightning.

## How To Learn
The best way to learn PyTorch Gale is to go through the documentation. You should probably get familiar with [PyTorch](https://pytorch.org/) and [PyTorch Lightning](https://pytorch-lightning.readthedocs.io/en/latest/). Next, go through [Hydra docs](https://hydra.cc/docs/next/intro) and [PyTorch Image Models](https://github.com/rwightman/pytorch-image-models)

## Getting Started (Documentation)
My current documentation for `PyTorch` Gale covers the basics. It is still getting updated. I plan to add more tutorials and examples in the comming weeks

## Contributions
Have a question? Found a bug? Missing a specific feature? Ran into a problem? Feel free to file a new issue or PR with respective title and description. If you already found a solution to your problem, don't hesitate to share it. Suggestions for new best practices and tricks are always welcome!

After you clone this repository, please run `nbdev_install_git_hooks` in your terminal. This sets up git hooks, which clean up the notebooks to remove the extraneous stuff stored in the notebooks (e.g. which cells you ran) which causes unnecessary merge conflicts.

## Quick recipes [WIP]

## Tests
To run the tests in parallel, launch:

`nbdev_test_nbs`

For all the tests to pass, you'll need to install the `gale[dev]`.

Tests are written using `nbdev`.
