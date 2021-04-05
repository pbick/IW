# Imports
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import time
import os
import copy
import sys

from train import train
from load_data import load_data

# -------------------------------------------------------------------------------------------------------------------------
# Script to initialize model and train it as a fixed feature extractor.
# Puts together the various methods in load_data, train, and visualize_model
# This code was obtained from the PyTorch Transfer Learning for Computer Vision Tutorial by Sasank Chilamkurthy
# Source: https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
# -------------------------------------------------------------------------------------------------------------------------

def main(data_dir):
    loaded_data = load_data(data_dir)
    dataloaders, dataset_sizes, class_names, device = loaded_data

    # Use resnet18 model pretrained on ImageNet
    model = torchvision.models.resnet18(pretrained=True)
    for param in model.parameters():
        param.requires_grad = False

    # Parameters of newly constructed modules have requires_grad=True by default
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs,  len(class_names))

    model = model.to(device)
    criterion = nn.CrossEntropyLoss()

    # Observe that only parameters of final layer are being optimized as
    # opposed to before
    optimizer = optim.Adam(model.fc.parameters(), lr=0.001)

    # Decay learning rate by a factor of 0.1 every 10 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

    # Train and evaluate
    model = train(model, criterion, optimizer, exp_lr_scheduler, loaded_data, num_epochs=100)

if __name__ == "__main__":
    data_dir = sys.argv[1]
    print("Data directory:", data_dir)
    main(data_dir)