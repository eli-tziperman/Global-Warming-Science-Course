#!/bin/sh
# Run all codes for teaching staff to produce data and images for
#    students, save data and figures, and move needed data to Data folder
#    for students.
# To runs this, must first cd to folder
#    Sources/Temperature/code-for-teaching-staff/

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

# process raw data files:
python read_Mann_etal_hockeystick_temperature_timeseries_ascii_write_npy.py
jupyter nbconvert --to notebook --inplace --execute prepeare_temperature_data_for_students.ipynb
# pickle variables for students:
python pickle_vars_for_students.py

#python convert_land_mask_from_ascii_to_npy.py
#python get_radiative_forcing_from_RCP85_for_1765_2500.py
#python read_RCP_scenarios_netcdf_SAT_plot_and_save.py
#python convert_GISS_Temperature_lon_lat_time_from_nc_to_npy.py
#python generate_hiatus_graphs_from_sine_or_control_run_plus_linear_trend.py
#python plot_Temperature_vs_lat_and_vs_time_ocean_land_RCP_scenarios.py
#python calculate_temperature_anomaly_timeseries_for_obs_and_RCP_scenarios.py
#python plot_zonally-averaged_RCP85_warming.py

