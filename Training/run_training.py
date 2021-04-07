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

def main(data_dir, exp_name):
    n_epochs = 100
    batch_size = 16
    l_rate = 0.0001
    wt_decay = 0.001
    lr_step = 10
    lr_gamma = 0.1
    lines = [f"num_epochs = {n_epochs}\n",
             f"batch_size = {batch_size}\n",
             f"lr = {l_rate}\n",
             f"weight_decay = {wt_decay}\n",
             f"lr_decay step_size = {lr_step}\n",
             f"lr_decay gamma = {lr_gamma}\n",
    ]

    with open(f"/home/pbickenbach/IW/Training Results/{exp_name}/hyper_params.txt", 'w') as f:
        f.writelines(lines)

    loaded_data = load_data(data_dir, batch_sz=batch_size)
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
    optimizer = optim.Adam(model.fc.parameters(), lr=l_rate, weight_decay=wt_decay)

    # Decay learning rate by a factor of 0.1 every 10 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=lr_step, gamma=lr_gamma)

    # Train and evaluate
    model = train(model, criterion, optimizer, exp_lr_scheduler, loaded_data, num_epochs=n_epochs)

if __name__ == "__main__":
    data_dir = sys.argv[1]
    exp_name = sys.argv[2]
    print("Data directory:", data_dir)
    main(data_dir, exp_name)