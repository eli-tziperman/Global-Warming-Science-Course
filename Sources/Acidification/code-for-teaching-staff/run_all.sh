#!/bin/bash
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

#cd ~/Dropbox/Courses/EPS101/Sources/Acidification/code-for-teaching-staff/

\rm -rf Output/to-pickle/*.npy
python carbonate_species_as_func_of_pH_K_as_func_of_T_EXACT.py
python process_pH_obs_and_rcp85.py
dir=../../Greenhouse/code-for-teaching-staff/Output/to-pickle/
cp -p $dir/CO2_observed.npy $dir/CO2_observed_years.npy \
   $dir/CO2_rcp85.npy $dir/CO2_rcp85_years.npy Input-from-greenhouse-module/
python get_CO2_from_Greenhouse_module.py
python pickle_vars_for_students.py
python Ksp_as_func_of_T_and_P.py
