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
mkdir -p Output/thickness_npy
mkdir -p Output/age_npy
\rm -rf Output/heff*.dat
\rm -rf Output/thickness_npy/*.npy
\rm -rf Output/age_npy/*.npy
\rm -rf Output/to-pickle/*

python process_thickness_data_all_years_cloud.py
\cp Output/thickness_npy/sic_thickness_obs1979.npy Output/to-pickle/
\cp Output/thickness_npy/sic_thickness_obs2024.npy Output/to-pickle/

python process_area_and_extent_timeseries_data_NSIDC.py

python process_age_data_all_years_cloud.py
\cp Output/age_npy/sic_age_obs1984.npy Output/to-pickle/
\cp Output/age_npy/sic_age_obs2024.npy Output/to-pickle/

set +e
python process_RCP85_data_cloud.py
set -e

python process_seaice_concentration_data_cloud.py

python process_long_CESM_control_cloud.py

python pickle_vars_for_students.py

# update plots for notes (need to then copy them from Output/ to
# ../notes/Figures/):
python plot_age_and_thickness_category_timeseries.py

# clean temporary files:
\rm -rf ~/Courses/EPS101/Data-for-teaching-staff/Sea-ice/Output/thickness_npy
\rm -rf ~/Courses/EPS101/Data-for-teaching-staff/Sea-ice/Output/age_npy
#\rm -rf ~/Courses/EPS101/Data-for-teaching-staff/Sea-ice/Output/to-pickle/*
