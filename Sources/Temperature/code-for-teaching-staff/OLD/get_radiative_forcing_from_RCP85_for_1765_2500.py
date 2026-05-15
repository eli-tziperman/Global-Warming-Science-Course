"""
This script creates the file radiative_forcing.npy, which contains a
time series of radiative forcing values for RCP8.5 from 1765 to 2500

Requirements:
    Requires data from http://www.pik-potsdam.de/~mmalte/RCPs/ 
    (Row "RCP 8.5", column "Global Annual Mean Radiative Forcing")
    **The file must be modified such that lines 1-60 (The text, non-data
    portion of the file) are either deleted or are prefaced with ";"**

Output Format:
    The file radiative_forcing.npy is a 2D, 2-row time series numpy array 
    of floats. The first row (array[0]) contains a 1D array of years from 
    1765 to 2500, in increments of one. The second row (array[1]) contains 
    a 1D array of corresponding radiative forcing values (for the RCP 8.5 
    scenario)
    radiative_forcing.npy may be loaded by using the function
    numpy.load("path/to/radiative_forcing.npy")

Usage Instructions:
    To use, set the variable RADFORCING_DATA_PATH (found directly
    below this __doc__ string) to be the path to the data described in
    Requirements.
    Run the script. After the data has been saved, it will be plotted.
    The script will not terminate until the plot is closed.

Yonathan Vardi 2019-07-17
"""
########################################################################
RADFORCING_DATA_PATH = "../../../Data-for-teaching-staff/Temperature/RCP85_MIDYEAR_RADFORCING.DAT"
########################################################################

import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

#open the data file
file = open(RADFORCING_DATA_PATH, "r")
raw_string = file.read()
file.close()

#convert the data file to the desired array
raw_string = raw_string.splitlines()
years = []
forcings = []
for i in raw_string:
    #skip comments or whitespace-only lines
    if i.startswith(";"):
        continue
    parts = i.split()
    if len(parts) == 0:
        continue
    
    #convert it to floats
    parts = list(map(float, parts))
    #append the year
    years.append(parts[0])
    #append the net forcing (this is found directly after the year)
    #*each line contains several different net forcings, and then the
    # individual components. The desired value is in index 1.
    forcings.append(parts[1])
#create the time series in format of timeseries[0]=years, timeseries[1]=forcings
timeseries = np.asarray([
    np.asarray(years),
    np.asarray(forcings)
])

#save it
OUTPUT_PATH = "./Output/radiative_forcing.npy"
np.save(OUTPUT_PATH, timeseries)
print("Data saved to " + OUTPUT_PATH)
#plot it to confirm correctness
plt.title("Radiative Forcing, RCP8.5")
plt.xlabel("Year")
plt.ylabel("Watts/m^2")
plt.plot(timeseries[0], timeseries[1])
plt.savefig("Output/Figures/temperature-Radiative_Forcing_RCP85.pdf",format='pdf');

plt.draw()
