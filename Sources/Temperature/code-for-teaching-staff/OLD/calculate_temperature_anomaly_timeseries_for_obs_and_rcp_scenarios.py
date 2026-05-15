"""
A small script that calculates the anomaly between all RCP time series
and the 1951-1980 time-mean (same one used by GISTEMP).

The calculated series are saved as "sat_anomaly.npy" in their respective 
("RCP26", "RCP45", "RCP85") folders in ./Output/

Yonathan Vardi 7/12/2019; further work by Eli, 2024/02
"""

RCP26_FILEPATH = "Output/RCP26/RCP26_GMST_annual_anomaly_timeseries.npy"
RCP45_FILEPATH = "Output/RCP45/RCP45_GMST_annual_anomaly_timeseries.npy"
RCP85_FILEPATH = "Output/RCP85/RCP85_GMST_annual_anomaly_timeseries.npy"

import numpy as np
from math import radians
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import griddata
from numpy import linalg
from scipy import stats
from scipy.stats import linregress
from scipy.signal import savgol_filter # for smoothing time series
from scipy.interpolate import griddata
from scipy import optimize
import copy

plt.ioff()

# read Hadley surface temperature since 1850 and calculate annual average:
# ------------------------------------------------------------------------
dataset = pd.read_csv('../../../Data-for-teaching-staff/Temperature/Hadley-SST/HadCRUT5.0Analysis_gl.txt'\
     ,sep='\\s+',na_values='NaN',comment='#' \
     ,skipinitialspace=True,skip_blank_lines=True,header=None)
data = np.asarray(dataset.iloc[:, :].values)
obs_Temperature_time_series_years=data[0::2,0]
obs_Temperature_time_series=data[0::2,13]
#header = dataset.iloc[:, :].columns
mean =np.mean(obs_Temperature_time_series[\
        np.logical_and(obs_Temperature_time_series_years>=1951 \
               ,obs_Temperature_time_series_years<=1980)])


########################################################################
# subtract GISS GMST avearged over 1960-1991 from RCP data, add it to
# 2005 data for obs and plot it:
########################################################################

# load the RCP26 data
RCP26 = np.load(RCP26_FILEPATH)
# turn it into an anomaly
RCP26[1] -=  13.974+273.15
# save it
np.save("./Output/RCP26/RCP26_GMST_annual_anomaly_timeseries.npy", RCP26)
# plot it to confirm validity of data
plt.plot(RCP26[0], RCP26[1], label="RCP2.6")

# load the RCP45 data
RCP45 = np.load(RCP45_FILEPATH)
# turn it into an anomaly
RCP45[1] -= 13.974+273.15
# save it
np.save("./Output/RCP45/RCP45_GMST_annual_anomaly_timeseries.npy", RCP45)
# plot it to confirm validity of data (exclude last 200 years because
# this one is longer than the rest)
plt.plot(RCP45[0, :-200], RCP45[1, :-200], label="RCP4.5")

# load the RCP85 data
RCP85 = np.load(RCP85_FILEPATH)
# turn it into an anomaly
RCP85[1] -= 13.974+273.15
# save it
np.save("./Output/RCP85/RCP85_GMST_annual_anomaly_timeseries.npy", RCP85)
# plot it to confirm validity of data
plt.plot(RCP85[0], RCP85[1], label="RCP8.5")

# save observed timeseries and corresponding year-range to npy file:
temperature_obs_annual_anomaly_timeseries=np.zeros((2,len(obs_Temperature_time_series_years)))
temperature_obs_annual_anomaly_timeseries[0,:]=obs_Temperature_time_series_years
temperature_obs_annual_anomaly_timeseries[1,:]=obs_Temperature_time_series
np.save("Output/OBS_GISS_GMST_annual_anomaly_timeseries.npy" \
    ,temperature_obs_annual_anomaly_timeseries)
# plot it
plt.plot(obs_Temperature_time_series_years, obs_Temperature_time_series \
         , color="maroon", label="Observed")

# plot a line across 0
plt.axhline(y=0, color="black", label="1951-1980 mean")

# show labels and legend
plt.legend()
plt.title("Observed and Projected Surface Air Temperature Anomaly")
plt.ylabel("Anomaly (C)")
plt.xlabel("Year")
plt.savefig("Output/Figures/temperature-Observed_and_Projected_Surface_Air_Temperature_Anomaly.pdf",format='pdf');

# show plot
plt.show()
