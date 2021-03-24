#
# Script to split Serengeti images into train/val and test datasets.
# Based on the splits generated in train_images.json and test_images.json
# Requires that a copy of the 'Downloads' directory is made.
#

import os
import json

orig_dir = "Downloads copy" # once again, make a copy of the 'Downloads' directory
os.makedirs("Datasets/trainval", exist_ok=True)
os.makedirs("Datasets/test", exist_ok=True)

with open("train_images.json") as f:
    data_train = json.load(f)

with open("test_images.json") as f:
    data_test = json.load(f)

for name in data_train:
    os.makedirs(f"Datasets/trainval/{name}", exist_ok=True)
    os.makedirs(f"Datasets/test/{name}", exist_ok=True)
    train_images = data_train[name]
    test_images = data_test[name]

    for im in train_images:
        fn = im["file_name"].split('/')[-1]
        os.rename(f"{orig_dir}/{name}/{fn}", f"Datasets/trainval/{name}/{fn}")
    
    for im in test_images:
        fn = im["file_name"].split('/')[-1]
        os.rename(f"{orig_dir}/{name}/{fn}", f"Datasets/test/{name}/{fn}")

print("Done! Now printing image counts for each folder")
for name in data_train:
    print("Species:", name)
    print("Train/val image count:", len(os.listdir(f"Datasets/trainval/{name}")))
    print("Test image count:", len(os.listdir(f"Datasets/test/{name}")))