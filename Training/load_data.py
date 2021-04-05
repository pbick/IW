# Imports
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
from ImageFolderWithPaths import ImageFolderWithPaths
import matplotlib.pyplot as plt
import time
import os
import copy

# -------------------------------------------------------------------------------------------------------------------------
# This code was obtained from the PyTorch Transfer Learning for Computer Vision Tutorial by Sasank Chilamkurthy
# Source: https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
# However, the following modifications were made:
# INCLUDE MODIFICATIONS HERE
# -------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------
# Load data using torchvision and torch.utils.data package
# ---------------------------------------------------------------------
def load_data(data_dir):
    # Data augmentation and normalization for training (actually only normalization for now)
    # Just normalization for validation
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    image_datasets = {x: ImageFolderWithPaths(os.path.join(data_dir, x),
                                        data_transforms[x])
                for x in ['train', 'val']}
    dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=16, # what batch size? 10? 128?
                                        shuffle=True, num_workers=4)
                for x in ['train', 'val']}
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
    class_names = image_datasets['train'].classes
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    return dataloaders, dataset_sizes, class_names, device

# ---------------------------------------------------------------------
# Method for visualizing images
# ---------------------------------------------------------------------
def imshow(inp, title=None):
    """Imshow for Tensor."""
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(0.001)  # pause a bit so that plots are updated

# ---------------------------------------------------------------------
# Main method
# In this case, it is used to visualize a few training and val 
# images to understand the augmentations and normalizations
# ---------------------------------------------------------------------
if __name__ == "__main__":
    data_dir = "../Datasets/"
    dataloaders, dataset_sizes, class_names, device = load_data(data_dir)

    # Get a batch of training data
    print("Getting a batch of training data...")
    inputs, classes, filenames = next(iter(dataloaders['train']))

    # Make a grid from batch
    out = torchvision.utils.make_grid(inputs)

    imshow(out, title=[class_names[x] for x in classes])
    print("Train filenames")
    print(filenames)
    plt.ioff()
    plt.show()

    # Get a batch of validation data
    print("Getting a batch of validation data...")
    inputs, classes, filenames = next(iter(dataloaders['val']))

    # Make a grid from batch
    out = torchvision.utils.make_grid(inputs)

    imshow(out, title=[class_names[x] for x in classes])
    print("Val filenames")
    print(filenames)