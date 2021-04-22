# 
# Script to visualize incorrect detections (in local machine)
#

import os
import json
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

incorrects_filename = "/Users/pbick/Documents/Princeton/Spring 2021/IW/Testing/Results/test_sse/detection_incorrects.json"
dataset_dir = "/Users/pbick/Documents/Princeton/Spring 2021/IW/Datasets/test_sse"

with open(incorrects_filename) as f:
    data = json.load(f)

print("Showing incorrect empty predictions...")
for im in data["empty"]:
    rel_fn = im["fn"].split('/')[-2] + "/" + im["fn"].split('/')[-1]
    truth = im["truth"]
    pred = im["pred"]
    full_fn = os.path.join(dataset_dir, rel_fn)

    img = mpimg.imread(full_fn)
    plt.imshow(img)
    plt.title(f"Fn: {rel_fn}\nPred: {pred}\nTruth: {truth}")
    plt.show()

print("Showing incorrect animal predictions...")
for im in data["animal"]:
    rel_fn = im["fn"].split('/')[-2] + "/" + im["fn"].split('/')[-1]
    truth = im["truth"]
    pred = im["pred"]
    full_fn = os.path.join(dataset_dir, rel_fn)

    img = mpimg.imread(full_fn)
    plt.imshow(img)
    plt.title(f"Fn: {rel_fn}\nPred: {pred}\nTruth: {truth}")
    plt.show()