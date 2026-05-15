"""
A script to extract the surface temperature anomaly data from a .nc
file. This script was specifically designed to work with the GISTEMP
dataset, and will likely not work as-is with others.

Output:
    This script outputs the files:

    'temperature_obs_GISS_anomaly_map_yearly.npy' - A yearly time series of 
        surface temperature anomaly maps from 1880 to 2018
    'temperature_obs_GISS_anomaly_map_axes.npy' - The longtitude and latitude 
        axes labels (Identical for both maps)
    
    the map file contains 3D numpy arrays. The first axis of the arrays is
    time since 1880, measured in months for one and years for the other.
    The second axis is latitude, and the third axis is longtitude.

        array[time, latitude, longtitude]

    The array within temperature_obs_GISS_anomaly_map_axes.npy is formatted
    differently. It is a 2D, 2-row numpy array. Its first index (axes[0])
    contains an array of labels for the latitude axis of either map, and 
    its second index (axes[1]) contains an array of labels for the 
    longtitude axis of either map.

    All files are created within ./Output/

Usage Instructions:
    To use this script, set the value of the global variable PATH
    directly below this __doc__ string to be the filepath to a .nc
    file containing surface temperature data.
    Set TEMPER_VAR_NAME to be the name of the variable within the .nc
        file that contains the 3D temperature data
    Set LAT_VAR_NAME to be the name of the variable within the .nc file
        that contains the latitude axis
    Set LON_VAR_NAME to be the name of the variable within the .nc file
        that contains the longtitude axis
    Set START_YEAR to be the first year for which there is data

    Run the script. The .npy files described in the Output section of
    this __doc__ string will be produced, and then be loaded. An
    animation will begin playing to confirm the saved data. Hold any
    key to stop the animation.

Yonathan Vardi 2019-07-11
"""
########################################################################
#
PATH = "../../../Data-for-teaching-staff/Temperature/gistemp1200_GHCNv4_ERSSTv5.nc"
TEMPER_VAR_NAME = "tempanomaly"
LAT_VAR_NAME = "lat"
LON_VAR_NAME = "lon"
START_YEAR = 1880
#
########################################################################

import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import sys

from netCDF4 import Dataset

# open the .nc file
ncfile = Dataset(PATH, 'r')

########################################################################

def find_total_mask(masked_3d_map):
    """
    Calculate the total of all the masks in a 3D map added across the
        time axis

    Params:
        masked_3d_map- A 3D numpy masked array representing a series of
            anomaly maps

    Return a 2D array of booleans
    """
    mask = np.full(masked_3d_map[0].shape, False, dtype=bool)
    for i in range(len(masked_3d_map)):
        mask = np.bitwise_or(mask, masked_3d_map[i].mask)
    return mask

######################################################### variable setup

# load the latitude and the longtitude axes from the file
lat_axis = ncfile.variables[LAT_VAR_NAME][:]
lon_axis = ncfile.variables[LON_VAR_NAME][:]

# load the monthly anomaly map
# last five months of anomaly map are sliced off so it ends on december
anomaly_map_monthly = ncfile.variables[TEMPER_VAR_NAME][:-5]

# create the yearly anomaly map by averaging every group of 12 months
anomaly_map_yearly = []
anomaly_map_yearly_mask = []    #this ensures that masked values are preserved
for i in range(0, len(anomaly_map_monthly), 12):
    months = anomaly_map_monthly[i:i+12]    #group of 12 months
    anomaly_map_yearly_mask.append(find_total_mask(months))
    anomaly_map_yearly.append(np.ma.mean(months, axis=0))
#create array with mask
anomaly_map_yearly = np.ma.array(anomaly_map_yearly, mask=anomaly_map_yearly_mask)
del anomaly_map_yearly_mask #no more need for this variable

# finally, ensure that masked values are mapped to NaN in both yearly and
# monthly anomaly maps
anomaly_map_monthly = np.ma.filled(anomaly_map_monthly, np.nan)
anomaly_map_yearly = np.ma.filled(anomaly_map_yearly, np.nan)

################################################################# saving

# save yearly values
np.save("./Output/temperature_obs_GISS_anomaly_map_yearly", anomaly_map_yearly)

# save axes (for plotting, shared between both maps)
saved_axes= np.empty(2, dtype=object)
saved_axes[0] = lat_axis
saved_axes[1] = lon_axis
np.save("./Output/temperature_obs_GISS_anomaly_map_axes", saved_axes)

