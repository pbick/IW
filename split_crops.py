# 
# Script to split crops into train and val datasets
# Splits based on folds
#

import json
import os

folds_filename = "Detection Results/folds.json"
with open(folds_filename) as f:
    folds = json.load(f)

def get_fold_from_loc(loc):
    for fold in folds:
        if loc in folds[fold]:
            return fold

crops_dir = "Crops/trainval"
dest_dir = "Datasets"
species_list = ["empty", "leopard", "lion", "elephant", "buffalo", "waterbuck", "hyenaspotted"]

for species in species_list:
    os.makedirs(os.path.join(dest_dir, "train", species), exist_ok=True)
    os.makedirs(os.path.join(dest_dir, "val", species), exist_ok=True)
    orig_dir = os.path.join(crops_dir, species)
    crops = os.listdir(orig_dir)

    for crop in crops:
        loc = crop.split("_")[-7]
        fold = get_fold_from_loc(loc)
        ds = "val" if fold == "1" else "train"
        orig_fn = os.path.join(orig_dir, crop)
        dest_fn = os.path.join(dest_dir, ds, species, crop)
        os.rename(orig_fn, dest_fn)