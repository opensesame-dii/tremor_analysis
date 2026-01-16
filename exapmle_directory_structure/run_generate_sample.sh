#! /bin/bash
# This script generates example files for the tremor_analysis package.

# pair file
mkdir -p target_dir/measurement_1_pair
python generate_sample_file.py target_dir/measurement_1_pair/left.csv
python generate_sample_file.py target_dir/measurement_1_pair/right.csv
# single file
mkdir -p target_dir/measurement_2_single
python generate_sample_file.py target_dir/measurement_2_single/measurement.csv
