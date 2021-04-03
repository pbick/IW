#
# Quick script for printing image counts per fold and per species per fold
#

import json
import csv 
import numpy as np 
import os

num_folds = 5
folds = {f"{fold}":[] for fold in range(1, num_folds+1)}

def get_fold_from_loc(loc):
    for fold in folds:
        if loc in folds[fold]:
            return fold

csv_filename = "fold_assignments.csv"
with open(csv_filename) as f:
    csv_reader = csv.reader(f, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            loc = row[0]
            fold = row[3]
            folds[fold].append(loc)
            line_count += 1

species_list = ["empty", "leopard", "lion", "elephant", "buffalo", "waterbuck", "hyenaspotted"]
fold_counts = {fold:{species:0 for species in species_list} for fold in folds}

data_fn = "detection1_results_clean.json"
with open(data_fn) as f:
    data = json.load(f)

for im in data["images"]:
    species = im["file"].split('/')[-2]
    loc = im["file"].split("_")[-3]
    fold = get_fold_from_loc(loc)
    fold_counts[fold][species] += 1

for fold in fold_counts:
    print(f"Fold #{fold}")
    for species in fold_counts[fold]:
        print(f"# of images for {species}:", fold_counts[fold][species])
    print()
