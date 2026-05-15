#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

#cd ~/Dropbox/Courses/EPS101/Sources/Ocean-circulation/code-for-teaching-staff/

\rm -rf Output/to-pickle/*.npy
python prepare_RAPID_data.py
python prepare_AMOC_GFDL_data_cloud.py
python plot_RCP85_SST_warming_map_cloud.py
python pickle_vars_for_students.py
