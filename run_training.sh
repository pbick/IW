
#!/bin/bash

# Script for running training on the GCP VM instance.
# Two command-line arguments: directory with datasets and experiment name.
# Uses nohup to run process without monopolizing shell. 

nohup python ~/IW/Training/run_training.py $1 > $2.out 2> $2.err &