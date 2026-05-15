#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

cd ~/Courses/EPS101/Sources/Hurricanes/code-for-teaching-staff/

mkdir -p Output
mkdir -p Output/Figures

python read_hurdat_data_calc_PDI.py
python calc_MDR_SST_historical_and_RCP85_cloud.py
python calc_plot_frac_major_hurricanes_regression_for_HURDAT.py

# get time series of number of Atlantic hurricanes:
python read_hurricanes_number_data.py

# make pickle data file for students:
python pickle_vars_for_students.py

echo "done preparing data for students, now some plots for the textbook:"

python hurricanes_ElNino_LaNina_jet_composites_ERA5_cloud.py
