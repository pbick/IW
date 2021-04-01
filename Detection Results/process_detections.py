# 
# Script to process the output of the MegaDetector.
# Computes the precision and recall for both the "empty" and "animal" categories
# Cleans up the detector results by discarding detections below the confidence threshold
# as well as the "human" and "vehicle" detection categories.
#

import numpy as np 
import json
import os

discard_incorrects = True
skip_rhinos = True
detection_filename = "detection1_results.json"
output_filename = detection_filename.split(".")[0] + "_clean.json"
incorrects_filename = detection_filename.split("_")[0] + "_incorrects.json"
print("Output filename:", output_filename)
print("Incorrects filename:", incorrects_filename)
print()

with open(detection_filename) as f:
    data = json.load(f)

images = data["images"]
categories = data["detection_categories"]

clean_data = {}
clean_data["detection_categories"] = categories
clean_data["info"] = data["info"]

num_true_animals = 0
num_true_emptys = 0
num_empty_predictions = 0
num_animal_predictions = 0
num_emptys = 0
num_animals = 0

threshold = 0.8

clean_images = []
incorrect_preds = {
    "empty": [],
    "animal": []
}
for image in images:
    incorrect = False
    clean_image = {}
    fn = image["file"]
    detections = image["detections"]

    # Get ground truth category from filename
    true_cat = fn.split('/')[-2]
    if true_cat == "empty":
        num_emptys += 1
    elif true_cat == "rhinoceros" and skip_rhinos:
        # want to skip over rhino images
        continue
    else:
        num_animals += 1
        true_cat = "animal"
    
    # Process the image's detections
    clean_detections = []

    if len(detections) == 0: 
        # No detections - MD prediction is empty
        num_empty_predictions += 1
         
        if true_cat == "empty":
            # empty prediction is correct
            num_true_emptys += 1
        else:
            # empty prediction is incorrect
            pred = {"fn": fn, "truth": f"animal ({fn.split('/')[-2]})", "pred": "empty"}
            incorrect_preds["empty"].append(pred)
            incorrect = True

    # Must process detections (prediction could still be empty if all below threshold)
    else:
        # Discard all detections below threshold or whose category is not "1" == "animal"
        clean_detections = [detection for detection in detections if (detection["conf"] > threshold and detection["category"] == "1")]

        if len(clean_detections) == 0:
            # Once again, no detections - MD prediction is empty
            num_empty_predictions += 1

            if true_cat == "empty":
                # empty prediction is correct
                num_true_emptys += 1
            else:
                # empty prediction is incorrect
                pred = {"fn": fn, "truth": f"animal ({fn.split('/')[-2]})", "pred": "empty"}
                incorrect_preds["empty"].append(pred)
                incorrect = True
        else:
            # Prediction is animal
            num_animal_predictions += 1

            if true_cat == "animal":
                # animal prediction is correct
                num_true_animals += 1
            else:
                # animal prediction is incorrect
                pred = {"fn": fn, "truth": "empty", "pred": "animal"}
                incorrect_preds["animal"].append(pred)
                incorrect = True
    
    if not (incorrect and discard_incorrects):
        clean_image["file"] = fn
        clean_image["max_detection_conf"] = image["max_detection_conf"]
        clean_image["detections"] = clean_detections
        clean_images.append(clean_image)

clean_data["images"] = clean_images

# Done iterating over image detections
print("Finished processing detections\n")
print("Threshold:", threshold)
print()
print("Number of empty images:", num_emptys)
print("Number of animal images:", num_animals)
print()
print("Number of empty predictions:", num_empty_predictions)
print("Number of animal predictions:", num_animal_predictions)
print()
print("Number of true empty predictions:", num_true_emptys)
print("Number of true animal predictions:", num_true_animals)
print()

empty_precision = 1.0 * num_true_emptys / num_empty_predictions
empty_recall = 1.0 * num_true_emptys / num_emptys
empty_fscore = 2.0 / ((1.0/empty_precision) + (1.0/empty_recall))

animal_precision = 1.0 * num_true_animals / num_animal_predictions
animal_recall = 1.0 * num_true_animals / num_animals 
animal_fscore = 2.0 / ((1.0/animal_precision) + (1.0/animal_recall))

print("Category: empty")
print("Precision:", empty_precision)
print("Recall:", empty_recall)
print("F-score:", empty_fscore)
print()

print("Category: animal")
print("Precision:", animal_precision)
print("Recall:", animal_recall)
print("F-score:", animal_fscore)
print()

print("Number of incorrect empty predictions:", len(incorrect_preds["empty"]))
print("Number of incorrect animal predictions:", len(incorrect_preds["animal"]))
print()

print("Number of images with correct predictions:", len(clean_data["images"]))
print()

print("Saving files now...")
with open(output_filename, "w") as outfile1:
    json.dump(clean_data, outfile1, indent=1)

with open(incorrects_filename, "w") as outfile2:
    json.dump(incorrect_preds, outfile2, indent=1)