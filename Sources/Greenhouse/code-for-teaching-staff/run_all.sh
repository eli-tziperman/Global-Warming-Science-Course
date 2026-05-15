#!/bin/bash
# run all cases needed for creating data/ figures for students
# run this script from the terminal as:
# $ run_all.sh

\rm Output/*.pdf Output/to-pickle/*.npy 

python radiative_transfer.py 280 'CO2'

python radiative_transfer.py 560 'CO2'

# run again with all gases to create input for two_blackbodies_and_OLR.py:
python radiative_transfer.py 280 'CO2' 'CH4' 'H2O' 'O3'

mv Output/to-pickle/*all_gases*.npy Output/
cp Output/to-pickle/wavenumbers.npy Output/wavenumbers_all_gases.npy

python prepare_and_plot_CO2_data_past_and_rcp85.py

python pickle_vars_for_students.py

python two_blackbodies_and_OLR.py
