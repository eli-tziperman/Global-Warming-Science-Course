#!/bin/bash
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

# activate python environment for course:
#source /opt/anaconda3/etc/profile.d/conda.sh

mkdir -p Output
mkdir -p Output/to-pickle

python prepare_data_for_students_cloud.py
python combine_satelleite_and_Jevrejeva_annual_GMSL.py
python pickle_vars_for_students.py

echo "If all run fine, you can delete Output/to-pickle/*.npy to clean up and save space."
echo " "

echo "done preparing pickle file for students, now some additional images for the textbook..."

jupyter nbconvert --to notebook --inplace --execute plot_fingerprint_results.ipynb
python plot_Jevrejeva_etal_2008.py
python plot_satellite_and_RCP85_GMSL_time_series.py
