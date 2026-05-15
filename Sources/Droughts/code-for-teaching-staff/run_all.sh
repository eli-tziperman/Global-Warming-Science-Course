#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

mkdir -p Output/frames
\rm -f Output/frames/*
python animate_and_save_SW_timeseries_of_PDSI_from_NADA.py
\rm -f Output/frames/*

jupyter nbconvert --to notebook --inplace --execute read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation_cloud.ipynb
\rm -rf Output/ssp585/*

python read_plot_timeseries_to_verify_data.py

python read_and_plot_raw_tree_ring_data.py

python pickle_vars_for_students.py

#mv Output/PDSI_timeseries.npy ../code-for-students/Data/
