This is a description of the purpose and dependencies of every script. It is meant to allow someone unfamiliar with the code to reuse it, and to recreate the datasets used should they become lost or outdated.

Also included is a list linking every .npy file with the program that created it.

Yonathan Vardi

####################################################
.npy files:
####################################################
(* = can be either "26", "45", or "85")
rcp*/sat_global.npy..................read_RCP_scenarios_netcdf_SAT_plot_and_save.py
rcp*/sat_global_s.npy................read_RCP_scenarios_netcdf_SAT_plot_and_save.py
rcp*/sat_anomaly.npy.................calculate_temperature_anomaly_timeseries_for_rcp_scenarios.py
rcp*/lat_average_timeseries.npy......read_RCP_scenarios_netcdf_SAT_plot_and_save.py
rcp*/lat_average_year1.npy...........read_RCP_scenarios_netcdf_SAT_plot_and_save.py
observed/lat_average_timeseries.npy..read_RCP_scenarios_netcdf_SAT_plot_and_save.py
observed/lat_average_year1.npy.......read_RCP_scenarios_netcdf_SAT_plot_and_save.py
1507_year_anomaly.npy................read_Mann_etal_hockeystick_temperature_timeseries_ascii_write_npy.py
1951-1980_timemean.npy...............read_RCP_scenarios_netcdf_SAT_plot_and_save.py
temperature_anomaly_map_axes.npy.....convert_GISS_Temperature_lon_lat_time_from_nc_to_npy.py
temperature_anomaly_map_monthly.npy..convert_GISS_Temperature_lon_lat_time_from_nc_to_npy.py
temperature_anomaly_map_yearly.npy...convert_GISS_Temperature_lon_lat_time_from_nc_to_npy.py
land_mask.npy........................convert_land_mask_from_ascii_to_npy.py
radiative_forcing.npy................get_radiative_forcing_from_RCP85_for_1765_2500.py

####################################################
Scripts:
####################################################
* When multiple options are given and no time division
  is specified, use monthly data

########generate_line_sin_and_line_control_graphs.py
Purpose:
	The sole purpose of this script is to draw
	the graph from the Hiatus.pdf image.
Files created:
	None, unless plot is saved
Dependencies:
	This script requires a directory of netCDF files
	from a control run of a climate model. Variable is tas.
	The climate model and experiment used are 
	GFDL-CM3 piControl r1i1p1

########calculate_temperature_anomaly_timeseries_for_rcp_scenarios.py
Purpose:
	To convert .npy files created by red_netcdf_SAT_plot_and_save.py
	into anomalies of the 1951-1980 mean and to generate
	the graph pictured in obj_and_proj_SAT_anomaly.pdf
Files created:
	rcp26/sat_anomaly.npy
	rcp45/sat_anomaly.npy
	rcp85/sat_anomaly.npy
Dependencies:
	No direct dataset dependencies, but requires four
	.npy files:
	 - .npy time series of mean surface air temperatures
	   from RCP2.6, RCP4.5, and RCP8.5
	 - .npy 2D map of the 1951-1980 mean surface air temp.
	 - .npy 3D map of the yearly surface air temp. anomaly

########read_Mann_etal_hockeystick_temperature_timeseries_ascii_write_npy.py
Purpose:
	To create a .npy file containing a time series of
	the temperature anomaly from the last 1507 years
Files created:
	1507_year_anomaly.npy
Dependencies:
	Requires a specific text dataset found at the bottom of
	http://www.meteo.psu.edu/holocene/public_html/supplements/MultiproxyMeans07/
	(labeled as the data for the blue line in the 
	section where the effects of the seven potential 
	problematic proxies are discussed.) This set contains
	the temperature anomaly in yearly intervals since
	501 AD

########convert_GISS_Temperature_lon_lat_time_from_nc_to_npy.py
Purpose:
	To create 3D .npy files containing maps
	of the measured surface air temperature
	anomaly
Files created:
	temperature_anomaly_map_monthly.npy
	temperature_anomaly_map_yearly.npy
	temperature_anomaly_map_axes.npy
Dependencies:
	The GISTEMP dataset, 1200km smoothed,
	as a netCDF file
	(labeled "Land-Ocean Temperature Index,
	ERSSTv5, 1200km smoothing" on
	https://data.giss.nasa.gov/gistemp/

########read_RCP_scenarios_netcdf_SAT_plot_and_save.py
Purpose:
	To create .npy files containing smoothed
	and unsmoothed time series of surface air
	temperatures, to create .npy files files
	containing SAT as a function of latitude, 
	to generate useful plots related to the 
	data created.
Files created:
	timemean.npy (1951-1980_timemean.npy)
	rcp26/sat_global.npy
	rcp26/sat_global_s.npy
	rcp26/lat_average_timeseries.npy
	rcp26/lat_average_year1.npy
	rcp45/sat_global.npy
	rcp45/sat_global_s.npy
	rcp45/lat_average_timeseries.npy
	rcp45/lat_average_year1.npy
	rcp85/sat_global.npy
	rcp85/sat_global_s.npy
	rcp85/lat_average_timeseries.npy
	rcp85/lat_average_year1.npy
	observed/lat_average_timeseries.npy
	observed/lat_average_year1.npy
Dependencies:
	This script requires several directories of
	netCDF files containing surface air temperature data:
	 - Files from an RCP8.5 simulation
	   (used was GFDL-CM3 rcp85 r1i1p1)
	 - Files from an RCP4.5 simulation
	   (used was GFDL-CM3 rcp45 r1i1p1)
	 - Files from an RCP2.6 simulation
	   (used was GFDL-CM3 rcp26 r1i1p1)
	 - Files from a historical simulation
	   (used was GFDL-CM3 historical r1i1p1)
	It also requires the GISTEMP dataset as a netCDF file
	(labeled "Land-Ocean Temperature Index,
	ERSSTv5, 1200km smoothing" on
	https://data.giss.nasa.gov/gistemp/
	
########convert_land_mask_from_ascii_to_npy.py
Purpose:
	To convert a specific ASCII land mask to usable form
	(90x180 numpy array of bools, where True represents
	land and False water)
Files Created:
	land_mask.npy
Dependencies:
	Requires the file water_percent_1d.asc, downloadable at
	https://web.archive.org/web/20060831045533/http://islscp2.sesda.com/ISLSCP2_1/data/ancillary/land_water_masks_xdeg/land_water_masks_xdeg.zip
	
########plot_Temperature_vs_lat_and_vs_time_ocean_land_RCP_scenarios.py
Purpose:
	To plot warming as a function of latitude, and 
	plot temperature as a function of year, for all 
	combinations of {winter, summer} and {sea, land}, 
	for RCP scenarios 3.6, 4.5, and 8.5
Files Created:
	none, unless plots are saved
Dependencies:
	Requires a landmask for GFDL-CM3 or compatible 
	(CM2.X maps seem to work), in the format of a .nc file 
	(used: https://data1.gfdl.noaa.gov/CM2.X/faq/question_19.html ;
	https://data1.gfdl.noaa.gov/dods-data/gfdl_cm2_1/CM2.1U-D4_1860-2000-AllForc_H2/pp/land/static/sftlf_A1.static.nc )
	as well as .npy files containing monthly SAT maps for RCP 2.6, 4.5, and 8.5
	(.npy files created by read_RCP_scenarios_netcdf_SAT_plot_and_save)
	
########get_radiative_forcing_from_RCP85_for_1765_2500.py
Purpose:
	To create a time series of radiative forcing for the 
	RCP 8.5 scenario to be used by oceantemp.py
Files Created:
	radiative_forcing.npy
Dependencies:
	Requires ASCII data from http://www.pik-potsdam.de/~mmalte/rcps/ 
    (Row "RCP 8.5", column "Global Annual Mean Radiative Forcing")
    **The file must be modified such that lines 1-60 (The documentation, non-
	data portion of the file) are either deleted or are prefaced with ";".
	Else, the program will disastrously attempt to read them
	as radiative forcing data
