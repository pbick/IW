#
# Script to make a JSON file containing ground truth
# This JSON file will be populated with results as they are obtained in the pipeline. 
#

import json
import os
import sys

species_list = ['empty', 'leopard', 'waterbuck', 'hyenaspotted', 'buffalo', 'lion', 'elephant']

def make_results_json(orig_dir, exp_name):
    data = {}
    for species in species_list:
        ims = os.listdir(f"{orig_dir}/{species}")
        for im in ims:
            im_dict = {
                "ground_truth": species,
                "detection_pred": None,
                "classification_pred": None,
            }
            data[f"{species}/{im}"] = im_dict
    
    out_fn = f"IW/Testing/Results/{exp_name}/results.json"
    with open(out_fn, 'w') as outfile:
        json.dump(data, outfile, indent=1)

if __name__ == "__main__":
    orig_dir = sys.argv[1]
    exp_name = sys.argv[2]
    make_results_json(orig_dir, exp_name)
    print("Successfully made results_json!")
