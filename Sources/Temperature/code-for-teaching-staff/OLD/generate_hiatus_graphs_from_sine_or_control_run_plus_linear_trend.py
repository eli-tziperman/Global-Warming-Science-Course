"""
This program generates a graph of a linear trend plus both a sine wave
and the data from a control run of a climate simulation to demonstrate
the "hiatus".

To use, ensure that the variable HIATUS_DIR directly below this __doc__
string contains a valid path to a DIRECTORY containing data from the
control run of a climate model. The data should be in netCDF form, and
may be composed of either one or multiple .nc files. If there are
multiple .nc files in the directory, the script assumes their alphabetical
order is the same as their chronological order.

Yonathan Vardi 2019-07-12
"""
########################################################################
HIATUS_DIR = "../../../Data-for-teaching-staff/Temperature/picontrol_small/"
########################################################################

import matplotlib.pyplot as plt
import numpy as np
from math import radians
import os
from netCDF4 import Dataset

########################################################################
# Create and plot control surface air temperature data + linear trend
########################################################################
def conc_directory_into_map(directory, data_name):
    """
    Concatenate an entire directory of .nc files into a continuous map of
    SAT data
    
    Params:
        directory- str. The directory containing the netCDF files
            (final "/" included). All .nc files found in this 
            directory will be opened, and files are assumed to contain 
            data ordered chronologically by their name. That is, file 
            "b.nc" is assumed to be a direct continuation of the data 
            in "a.nc". Files are also assumed to have identically named 
            variables.
            (e.g "../../../Data-for-teaching-staff/Temperature/picontrol_small/")

        data_name- str. The name of the variable within the netCDF file
            which contains the SAT data.
    """

    #begin by making a list of all .nc files
    file_list=[]
    for i in os.listdir(directory):
        file_list.append(os.fsdecode(i))
    file_list.sort()

    filenames = []
    for file in file_list:
        if file.endswith(".nc"):
            filenames.append(directory + file)

    #ensure there were files in directory
    if len(filenames) == 0:
        print("No .nc files in directory!")
        return

    #then get the values from the first file
    ncfile = Dataset(filenames[0], 'r')
    map_to_return = ncfile.variables[data_name][:]

    #then add the data from the rest of the files
    for i in range(1, len(filenames)):
        ncfile = Dataset(filenames[i], 'r')
        print("concatenating " + filenames[i])
        map_to_return = np.ma.concatenate((map_to_return,
                            ncfile.variables[data_name][:]))

    #Then return the data
    return map_to_return

def get_mean_of_map(input_map):
    """Return the mean SAT from a given map, taking into account
    the Earth's curvature and the presence of land.
    
    Params:
        input_map- 2D numpy array of floats. This represents a global 
            map of SAT values in a given year.
    
    Return a float representing the mean SAT value in the map
    """
    lat_axis = list(range(-89, 90, 2))
    denominator = 0
    numerator = 0
    for i in range(input_map.shape[0]):
        weight = np.cos(radians(lat_axis[i]))
        s = np.sum(input_map[i])
        if s > 0 or s < 0:
            numerator += s * weight
            denominator += np.count_nonzero(input_map[i]) * weight
    return numerator/denominator

def convert_map_into_time_series(map_to_convert):
    series = []
    for i in range(len(map_to_convert)):
        series.append(get_mean_of_map(map_to_convert[i]))
    return np.asarray(series)

def convert_monthly_time_series_to_yearly(series):
    year_series = []
    for i in range(0, len(series), 12):
        months = series[i:i+12]
        year_series.append(np.mean(months))
    return np.asarray(year_series)

########################################################################
# Main Program:
########################################################################

# ----------------------------------------
# Create and plot sine wave + linear trend
# ----------------------------------------

plot_range = np.arange(0, 100, .05)
sin = 3*np.sin((2*np.pi/40)*plot_range)
linear = plot_range*.5
sin_linear = sin + linear

fig = plt.figure(figsize=(10,5))
sin_ax, control_ax = fig.subplots(1, 2)
plt.ioff()

sin_ax.plot(plot_range, sin, ":")
sin_ax.plot(plot_range, linear, ":")
sin_ax.plot(plot_range, sin_linear)
#hide the axes
sin_ax.set_xlabel('"years"')
sin_ax.set_ylabel('"Temperature"')
sin_ax.set_title("Sine + Linear Trend")

# --------------------------------------------------------------
#plot a monthly time series of global mean SATs from the control
#dataset of GFDL model with and without added linear trend:
# --------------------------------------------------------------
control_series = convert_map_into_time_series(
                    conc_directory_into_map(HIATUS_DIR, "tas"))
#convert the control series from monthly to yearly
control_series = convert_monthly_time_series_to_yearly(control_series)
# save control series to npy file for students:
np.save("Output/PIcontrol_GMST_annual_anomaly_timeseries.npy",control_series)
#convert the control series into an anomaly by subtractings its mean from it
control_series_mean = np.mean(control_series)
control_series -= control_series_mean
#The control dataset is measured in contextless years, so the only thing
#that matters is the LENGTH of the range
control_range = np.arange(1, 1+len(control_series))
#generate a linear trend based on the range
control_linear = control_range*.01
#combine the trend and the series
series_with_trend = control_linear + control_series

#plot!
control_ax.plot(control_range, control_series, ":")
control_ax.plot(control_range, control_linear, ":")
control_ax.plot(control_range, series_with_trend)

control_ax.set_ylabel("Temperature")
control_ax.set_xlabel("years")
control_ax.set_title("Control Data + Linear Trend")

try:
    os.mkdir("Output/Figures")
except OSError:
    print ("failed to create directory %s" % "Output/Figures, may have already existed")
else:
    print ("created directory %s " % "Output/Figures")
    
plt.savefig("Output/Figures/temperature-hiatus_from_variability_plus_linear_trend.pdf",format='pdf');

#show the plot
plt.draw()
