#!/bin/sh
# Run all codes for teaching staff to produce data and images for
# students, save data and figures, and move needed data to Data folder
# for students.
# Run this from Sources/Temperature/code-for-teaching-staff/

# echo commands to screen:
set -o verbose
# subsequent commands which fail will cause an immediate exit:
set -e

# process raw data files:
python read_Mann_etal_hockeystick_temperature_timeseries_ascii_write_npy.py

jupyter nbconvert --to notebook --inplace --execute prepeare_temperature_data_for_students.ipynb

python prepare_data_for_fingerprinting.py

# pickle variables for students:
python pickle_vars_for_students.py
