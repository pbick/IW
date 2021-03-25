#!/bin/bash

# Script for running the MegaDetector on the GCP VM instance.
# Only command-line argument is experiment name.
# Uses nohup to run process without monopolizing shell. 

nohup python ~/CameraTraps/detection/run_tf_detector_batch.py ~/md_v4.1.0.pb ~/IW/trainval ~/IW/$1_results.json --recursive > $1.out 2> $1.err &