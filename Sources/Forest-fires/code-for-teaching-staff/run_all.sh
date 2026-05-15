#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

jupyter nbconvert --to notebook --inplace --execute analyze_Australia_fires_King_etal_2020.ipynb
jupyter nbconvert --to notebook --inplace --execute analyze_west_US_fires_Abatzoglou_Williams_2016_data.ipynb
jupyter nbconvert --to notebook --inplace --execute prepare_canadian_fire_data_twbx_file.ipynb
jupyter nbconvert --to notebook --inplace --execute prepare_US_fire_data.ipynb
jupyter nbconvert --to notebook --inplace --execute prepare_global_MODIS_fire_data.ipynb
jupyter nbconvert --to notebook --inplace --execute plot_global_fires.ipynb

\cp ~/Courses/EPS101/EPS101-Cheyenne/Output/forest_fires_west_US_TS_ensemble_timeseries.npy ~/Courses/EPS101/EPS101-Cheyenne/Output/forest_fires_west_US_TS_timeseries_ensemble_years.npy Output/to-pickle/

python pickle_vars_for_students.py

echo "If everything ran OK, then can clean temporary files by:"
echo "cd ~/Courses/EPS101/Sources/Forest-fires/code-for-teaching-staff/Output/; \\rm sst.mnmean.nc to-pickle/*.npy"
