#
# Script to get overall pipeline results from experiment's results.json file
#

import json
import os
import sys 

species_list = ['empty', 'leopard', 'lion', 'elephant', 'buffalo', 'waterbuck', 'hyenaspotted']

def pipeline_results(exp_name):
    json_fn = f"Results/{exp_name}/results.json"
    with open(json_fn) as f:
        data = json.load(f)
    
    count_positives = {species:0.0 for species in species_list}
    count_predictions = {species:0.0 for species in species_list}
    count_true_positives = {species:0.0 for species in species_list}
    incorrect_detections = {'empty':0, 'animal': 0}

    ims_count = 0.0
    corrects_count = 0.0
    incorrects_count = 0.0
    incorrects_from_detector = 0.0
    incorrects_from_classifier = 0.0
    duplicates = 0.0

    for im in data:
        ims_count += 1.0
        im_dict = data[im]
        truth = im_dict['ground_truth']
        count_positives[truth] += 1.0
        # print(im)

        if truth == "empty":
            if im_dict['detection_pred'] == "empty":
                # detector correctly predicted "empty"
                corrects_count += 1.0
            elif len(im_dict["classification_pred"]) == 1 and truth in im_dict["classification_pred"]:
                incorrects_from_detector += 1.0
                corrects_count += 1.0
            else:
                incorrects_count += 1.0
                incorrects_from_detector += 1.0
                incorrects_from_classifier += 1.0
                duplicates += 1.0
        else: # truth is animal
            if im_dict['detection_pred'] == "empty":
                # detector incorrectly predicted "empty"
                incorrects_count += 1.0
                incorrects_from_detector += 1.0
            elif truth in im_dict["classification_pred"]:
                corrects_count += 1.0
            else:
                incorrects_count += 1.0
                incorrects_from_classifier += 1.0
    
    print("Finished processing")
    print("Num images:", ims_count)
    print("Num corrects:", corrects_count)
    print("Num incorrects:", incorrects_count)
    print("Pipeline accuracy:", corrects_count / ims_count)
    print()
    print("Incorrects from detector:", incorrects_from_detector)
    print("Incorrects from classifier:", incorrects_from_classifier)
    print("Count duplicates:", duplicates)



if __name__ == "__main__":
    exp_name = sys.argv[1]
    pipeline_results(exp_name)