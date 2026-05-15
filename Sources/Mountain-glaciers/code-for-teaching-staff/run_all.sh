#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

jupyter nbconvert --to notebook --inplace --execute Quelccaya_ice_core.ipynb

jupyter nbconvert --to notebook --inplace --execute WGMS.ipynb

python calc_snow_extent_NH.py

python pickle_vars_for_students.py
