#
# Script to get image and detection counts per camera trap location
# Writes to a csv file
#

import os
import json
import csv
import numpy as np 

detection_filename = "detection1_results_clean.json"
splits_filename = "../Data Management/SnapshotSerengetiSplits_v0.json"

with open(detection_filename) as f:
    detection_data = json.load(f)

with open(splits_filename) as f:
    splits_data = json.load(f)

training_locs = splits_data["splits"]["train"]

image_counts = {loc:0 for loc in training_locs}
detection_counts = {loc:0 for loc in training_locs}

for im in detection_data["images"]:
    loc = im["file"].split("_")[-3]
    num_detections = len(im["detections"])

    if num_detections > 0:
        # Only count images with detections
        image_counts[loc] += 1
        detection_counts[loc] += num_detections

total_ims = 0
print("Number of locations:", len(training_locs))
print("Image counts per location")
for loc in image_counts:
    print(f"{loc}: {image_counts[loc]}")
    total_ims += image_counts[loc]
print("Total number of images:", total_ims)
print("-------------------------------------------------------------------")

total_detections = 0
print("Detection counts per location")
for loc in detection_counts:
    print(f"{loc}: {detection_counts[loc]}")
    total_detections += detection_counts[loc]
print("Total number of detections:", total_detections)
print("-------------------------------------------------------------------")

csv_filename = "location_counts.csv"
with open(csv_filename, mode ='w') as outfile:
    fieldnames = ['location', 'image_count', 'detections_count']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for loc in image_counts:
        num_images = image_counts[loc]
        num_detecs = detection_counts[loc]
        assert num_images <= num_detecs
        writer.writerow({"location":loc, "image_count":num_images, "detections_count":num_detecs})
