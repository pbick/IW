# 
# Script to process the results of the classifier
#

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
from ImageFolderWithPaths import ImageFolderWithPaths
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
import os
import copy
import sys
import json

species_list = ['empty', 'leopard', 'waterbuck', 'hyenaspotted', 'buffalo', 'lion', 'elephant']

def load_data(data_dir):
    # Only testing
    data_transforms = transforms.Compose([
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    image_dataset = ImageFolderWithPaths(data_dir, data_transforms)
    dataset_size = len(image_dataset)
    dataloader = torch.utils.data.DataLoader(image_dataset, batch_size=dataset_size, shuffle=True, num_workers=1)
    class_names = image_dataset.classes
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    return (dataloader, dataset_size, class_names, device)

def process_classifications(model, loaded_data, exp_name):
    results_filename = f"~/IW/Testing/Results/{exp_name}/results.json"
    with open(results_filename) as f:
        results = json.load(f)

    dataloader, dataset_size, class_names, device = loaded_data
    was_training = model.training
    model.eval()

    images_processed = 0
    count_positives = {species:0.0 for species in species_list}
    count_predictions = {species:0.0 for species in species_list}
    count_true_positives = {species:0.0 for species in species_list}

    with torch.no_grad():
        for i, (inputs, labels, filenames) in enumerate(dataloader):
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            for j in range(inputs.size()[0]):
                images_processed += 1
                pred = class_names[preds[j]]
                truth = class_names[labels[j]]
                fn = filenames[j]
                rel_fn = os.path.join(truth, fn.split("___")[0])

                results[rel_fn]["classification_pred"].append(pred)
                count_positives[truth] += 1.0
                count_predictions[pred] += 1.0

                if pred == truth:
                    count_true_positives[pred] += 1.0
    
    total_true_positives = 0.0
    total_positives = 0.0
    print("Total images processed:", images_processed)
    for label in species_list:
        print("Species:", label)
        num_positives = count_positives[label]
        total_positives += num_positives
        print("Num Positives:", num_positives)
        num_predictions = count_predictions[label]
        print("Num Predictions:", num_predictions)
        num_true_positives = count_true_positives[label]
        total_true_positives += num_true_positives
        print("Num True Positives:", num_true_positives)
        precision = num_true_positives / num_predictions
        print("Precision:", precision)
        recall = num_true_positives / num_positives
        print("Recall:", recall)
        f_score = 2.0 / ((1.0/precision) + (1.0/recall))
        print("F-score", f_score)
        print()
    
    print("Model Accuracy", total_true_positives/total_positives)

    print()
    print("Printing positives counts")
    print(count_positives)

    with open(results_filename, 'w') as results_file:
        json.dump(results, results_file, indent=1)

if __name__ == "__main__":
    data_dir = sys.argv[1]
    exp_name = sys.argv[2]
    loaded_data = load_data(data_dir)

    model = torchvision.models.resnet18(pretrained=True)
    for param in model.parameters():
        param.requires_grad = False
    num_classes = len(loaded_data[2])
    num_ftrs = model.fc.in_features
    model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 256), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(256, num_classes), nn.LogSoftmax(dim=1))
    model = model.to(loaded_data[3])
    model.load_state_dict(torch.load("best_model.pt"))

    process_classifications(model, loaded_data, exp_name)
