#!/bin/bash

# Script for running the pipeline on a testing dataset
# Two command-line arguments: directory of testing dataset and experiment name.
# Uses nohup to run process without monopolizing shell. 

orig_dir=$1
exp_name=$2

# Make directory to store results
mkdir ~/IW/Testing/Results/$exp_name

# Make ground truth and results file
python ~/IW/Testing/make_results_json.py $orig_dir $exp_name

# Run detector
export PYTHONPATH="$PYTHONPATH:$PWD/ai4eutils:$PWD/CameraTraps"
python ~/CameraTraps/detection/run_tf_detector_batch.py ~/md_v4.1.0.pb ~/$orig_dir ~/IW/Testing/Results/$exp_name/detection_results.json --recursive

# Run script to process detections
python ~/IW/Testing/process_detections.py ~/IW/Testing/Results/$exp_name > ~/IW/Testing/Results/$exp_name/process_detections.out

# Make crops
mkdir ~/IW/Crops/$exp_name
mkdir ~/IW/Crops/$exp_name/empty ~/IW/Crops/$exp_name/leopard ~/IW/Crops/$exp_name/lion ~/IW/Crops/$exp_name/buffalo ~/IW/Crops/$exp_name/elephant ~/IW/Crops/$exp_name/waterbuck ~/IW/Crops/$exp_name/hyenaspotted
python ~/CameraTraps/classification/crop_detections.py ~/IW/Testing/Results/$exp_name/detection_results_clean.json ~/IW/Crops/$exp_name -i ~/$orig_dir -v 4.1 --square-crops -t 0.8 --logdir ~/IW/Crops/$exp_name

# Run classifier on crops
python ~/IW/Testing/process_classifications.py ~/IW/Crops/$exp_name $exp_name > ~/IW/Testing/Results/$exp_name/process_classifications.out
