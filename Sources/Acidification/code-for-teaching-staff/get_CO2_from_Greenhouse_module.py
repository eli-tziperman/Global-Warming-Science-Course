# get co2 pre-processed in the greenhouse module and saved there as
# npy files, extract only the years needed here.

import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
import matplotlib

# get CO2 pre-processed in Greenhouse module: (see run_all.sh script for source)
CO2_observed=np.load("Input-from-greenhouse-module/CO2_observed.npy")
CO2_observed_years=np.load("Input-from-greenhouse-module/CO2_observed_years.npy")
CO2_rcp85_input=np.load("Input-from-greenhouse-module/CO2_rcp85.npy")
CO2_rcp85_input_years=np.load("Input-from-greenhouse-module/CO2_rcp85_years.npy")

# get years in which pH is available:
pH_obs_years=np.load("Output/to-pickle/pH_obs_global_decadal_mean_years.npy")
pH_rcp85_years=np.load("Output/to-pickle/pH_rcp85_global_decadal_mean_years.npy")


# first, observed CO2 record:
# ---------------------------
CO2_obs_global_decadal_mean=pH_obs_years*0.0
CO2_obs_global_decadal_mean_years=pH_obs_years*0.0
for i in range(0,len(pH_obs_years)):
    # find the index of CO2_observed_years corresponding to year pH_obs_years[i]:
    iyear,=np.nonzero(CO2_observed_years.astype(int)==int(pH_obs_years[i]))
    # if there is such an index, store this CO2 value into CO2_obs_global_decadal_mean:
    if iyear.size>0:
        #print(i,pH_obs_years[i],iyear[0])
        CO2_obs_global_decadal_mean[i]=CO2_observed[iyear[0]]
        CO2_obs_global_decadal_mean_years[i]=CO2_observed_years[iyear[0]]

pH_obs_years=pH_obs_years[CO2_obs_global_decadal_mean!=0.0]
CO2_obs_global_decadal_mean=CO2_obs_global_decadal_mean[CO2_obs_global_decadal_mean!=0.0]



# second, rcp85 CO2 record:
# -------------------------
CO2_rcp85_global_decadal_mean=pH_rcp85_years*0.0
CO2_rcp85_global_decadal_mean_years=pH_rcp85_years*0.0
for i in range(0,len(pH_rcp85_years)):
    # find the index of CO2_rcp85_input_years corresponding to year pH_rcp85_years[i]:
    iyear,=np.nonzero(CO2_rcp85_input_years.astype(int)==int(pH_rcp85_years[i]))
    # if there is such an index, store this CO2 value into CO2_rcp85_global_decadal_mean:
    if iyear.size>0:
        #print(i,pH_rcp85_years[i],iyear[0])
        CO2_rcp85_global_decadal_mean[i]=CO2_rcp85_input[iyear[0]]
        CO2_rcp85_global_decadal_mean_years[i]=CO2_rcp85_input_years[iyear[0]]


# save arrays to be pickled:
# --------------------------
np.save("Output/to-pickle/CO2_obs_global_decadal_mean.npy",CO2_obs_global_decadal_mean)
np.save("Output/to-pickle/CO2_obs_global_decadal_mean_years.npy",CO2_obs_global_decadal_mean_years)
np.save("Output/to-pickle/CO2_rcp85_global_decadal_mean.npy",CO2_rcp85_global_decadal_mean)
np.save("Output/to-pickle/CO2_rcp85_global_decadal_mean_years.npy",CO2_rcp85_global_decadal_mean_years)
