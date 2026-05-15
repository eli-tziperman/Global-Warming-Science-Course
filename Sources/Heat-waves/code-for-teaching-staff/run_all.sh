#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

dir="../../../EPS101-Cheyenne/Output"
cp -p $dir/heat_waves_*.npy ./Output/to-pickle/
jupyter nbconvert --to notebook --inplace --execute prepare_Siberian_temperature_data.ipynb
# prepare the WBT figure for the notes:
jupyter nbconvert --to notebook --inplace --execute wet-bulb-temperature.ipynb

python pickle_vars_for_students.py
