#
# Script to create json file splitting Serengeti data into train/val and test based on recommended splits.
# Note that we are using the recommended val set as test,
# and the train set as train and val (will have to do k-fold cross validation.
#

import numpy as np 
import json
import os

with open("species_images.json") as f:
    data_species = json.load(f)

with open("empty_images.json") as f:
    data_empty = json.load(f)

with open("SnapshotSerengetiSplits_v0.json") as f:
    data_splits = json.load(f)

train_locs = data_splits["splits"]["train"]
test_locs = data_splits["splits"]["val"] # once again, remember that we are using their designated val as test

train_json = {}
test_json = {}

for name in data_species: 
    train_ims = [image for image in data_species[name] if image['location'] in train_locs]
    test_ims = [image for image in data_species[name] if image['location'] in test_locs]
    assert len(train_ims) + len(test_ims) == len(data_species[name])

    train_json[name] = train_ims
    test_json[name] = test_ims

empty_train_ims = [image for image in data_empty["empty"] if image['location'] in train_locs]
empty_test_ims = [image for image in data_empty["empty"] if image['location'] in test_locs]
assert len(empty_train_ims) + len(empty_test_ims) == len(data_empty["empty"])

train_json["empty"] = empty_train_ims
test_json["empty"] = empty_test_ims

# Now, discard the ones that were cleaned out
for name in train_json:
    clean_list = os.listdir(f"Downloads/{name}")
    train_json[name] = [image for image in train_json[name] if image["file_name"].split('/')[-1] in clean_list]
    test_json[name] = [image for image in test_json[name] if image["file_name"].split('/')[-1] in clean_list]

print("Printing image counts by species for train/val dataset")
for name in train_json:
    print(f"{name}: {len(train_json[name])}")

print("Printing image counts by species for test dataset")
for name in test_json:
    print(f"{name}: {len(test_json[name])}")

train_filename = "train_images.json"
with open(train_filename, "w") as outfile:
    json.dump(train_json, outfile)

test_filename = "test_images.json"
with open(test_filename, "w") as outfile:
    json.dump(test_json, outfile)