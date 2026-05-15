#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

python plot_tide_gauge_storm_surge_records.py
python plot_tide_gauge_and_precipitation_Houston_for_hurricane_Harvey.py
python precipitation_read_station_data_into_dictionary.py


# get extreme percipitation data from Cheyenne:
export DATA_DIR="../../../EPS101-Cheyenne/Output"
\cp -p $DATA_DIR/extreme_precip_*.npy \
   $DATA_DIR/wet_wetter_*.npy \
   $DATA_DIR/precipitation_*.npy \
  Output/to-pickle/

python pickle_vars_for_students.py
