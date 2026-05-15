This is a list of the purpose and dependencies of 
every script. It is meant to allow someone unfamiliar 
with the code to reuse it, and to recreate the datasets
used should they become lost or outdated.

Also included is a list linking every .npy file with 
the program that created it.

######################################################################
.npy files: (more details in dedicated file found in npy folder)
######################################################################
sahel_miroc_evaporation.npy   read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sahel_miroc_moisture.npy      read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sahel_miroc_precipitation.npy read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sahel_gfdl_evaporation.npy    read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sahel_gfdl_moisture.npy       read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sahel_gfdl_precipitation.npy  read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sw_miroc_evaporation.npy      read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sw_miroc_moisture.npy         read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sw_miroc_precipitation.npy    read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sw_gfdl_evaporation.npy       read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sw_gfdl_moisture.npy          read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
sw_gfdl_precipitation.npy     read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py

######################################################################
Scripts:
######################################################################
* When multiple options are given and no time division
  is specified, use monthly data

########read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
Purpose:
	Provides a class that extracts and organizes drought data
	for a given projected scenario.
	Uses the provided class to create plots and animation frames,
	as well as saving some of the data into .npy files.
Files Created:
	Frames for animations
	sahel_miroc_evaporation.npy
	sahel_miroc_moisture.npy
	sahel_miroc_precipitation.npy
	sahel_gfdl_evaporation.npy
	sahel_gfdl_moisture.npy
	sahel_gfdl_precipitation.npy
	sw_miroc_evaporation.npy
	sw_miroc_moisture.npy
	sw_miroc_precipitation.npy
	sw_gfdl_evaporation.npy
	sw_gfdl_moisture.npy
	sw_gfdl_precipitations.npy
	Output graphs are saved to Output/Figures
Dependencies:
	Each scenario initialized requires three separate datasets:
    evaporation, precipitation, and soil moisture. Each of 
	these datasets can be either a single .nc file or a 
	directory of .nc files which are direct chronological 
	continuations of each other.
	The RCP8.5 wet Sahel model used is MIROC-ESM-CHEM, and
	the dry Sahel model used is GFDL CM3.
	
########animate_PDSI_from_NADA.py
Purpose:
	Create frames for an animation of PDSI which can later be assembled
	by a program such as ffmpeg
Files created:
	Creates frames for an animation of historic PDSI in North America
Dependencies:
	Requires the PDSI file nada_hd2_cl.nc (NADA Dataset)
	
########read_plot_timeseries_to_verify_data.py
Purpose:
	Load and plot the .npy files created by other programs
	for the purpose of verifying their correctness
Files created:
	Output graph is saved to Output/Figures
Dependencies:
	Requires all 12 .npy files created by read_RCP85_write_and_plot_timeseries_of_moisture_evaporation_precipitation.py
	
########pickle_vars_for_students.py
Purpose:
	Process the .npy files created by other programs into a single pickle file
Files created:
	Creates variables.pickle. This file contains every .npy file
	found in Output/
	This file may be loaded to recreate the data in the .npy files 
	as variables whose name is the name of the file (without the .npy)
Dependencies:
	Strictly, only requires ./Output/ to exist; for proper functioning
	requires ./Output/ to contain the .npy files created by other programs