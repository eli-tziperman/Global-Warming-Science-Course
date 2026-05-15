import numpy as np
import matplotlib.pyplot as plt 
from math import *
from scipy.special import jv,yv
from scipy.integrate import quad
from scipy.special import wofz
import pandas as pd
import time
import sys
from math import isnan

# font required by PUP:,
plt.rcParams['font.family'] = 'Myriad Pro'

# first, ice core data for 1850-1958:
# ------------------------------------
file='../../../Data-for-teaching-staff/Greenhouse/CO2-timeseries/CO2_annual_1850_to_1960.txt'
dataset = pd.read_csv(file,na_values='NaN',sep='\\s+'
                      ,comment='#',skipinitialspace=False,skip_blank_lines=False
                      ,header=None)
data = np.asarray(dataset.iloc[:, :].values)
#header = dataset.iloc[:, :].columns

CO2_observed_1850_1958_years=data[:,0]
CO2_observed_1850_1958=np.asarray(data[:,1])
CO2_observed_1850_1958=1.0*CO2_observed_1850_1958[CO2_observed_1850_1958_years<1960]
CO2_observed_1850_1958_years=1.0*CO2_observed_1850_1958_years[CO2_observed_1850_1958_years<1960]


# second, data for 1959-now:
# --------------------------
file='../../../Data-for-teaching-staff/Greenhouse/CO2-timeseries/co2_mm_mlo.txt'
dataset = pd.read_csv(file,na_values='NaN',sep='\\s+'
                      ,comment='#',skipinitialspace=False,skip_blank_lines=False
                      ,header=None)
data = np.asarray(dataset.iloc[:, :].values)
#header = dataset.iloc[:, :].columns
CO2_observed_since_1959_years=data[:,2] # decimal time
CO2_observed_since_1959=data[:,3]
# keep only since 1959:
CO2_observed_since_1959=1.0*CO2_observed_since_1959[CO2_observed_since_1959_years>=1959]
CO2_observed_since_1959_years=1.0*CO2_observed_since_1959_years[CO2_observed_since_1959_years>=1959]
# An annual average version:
last_year=int(max(np.floor(CO2_observed_since_1959_years)))
CO2_annual_observed_since_1959_years=np.zeros((int(last_year-1959)))
CO2_annual_observed_since_1959=0.0*CO2_annual_observed_since_1959_years
i=0
for year in range(1959,last_year):
    data_one_year=CO2_observed_since_1959[np.floor(CO2_observed_since_1959_years)==year]
    CO2_annual_observed_since_1959[i] = np.mean(data_one_year)
    CO2_annual_observed_since_1959_years[i]=year
    i=i+1

# combine annual:
# ---------------
CO2_observed=1.0*np.concatenate((CO2_observed_1850_1958,CO2_annual_observed_since_1959))
CO2_observed_years=1.0*np.concatenate((CO2_observed_1850_1958_years,CO2_annual_observed_since_1959_years))
# combine partially annual partially monthly:
# -------------------------------------------
CO2_monthly_observed=1.0*np.concatenate((CO2_observed_1850_1958,CO2_observed_since_1959))
CO2_monthly_observed_years=1.0*np.concatenate((CO2_observed_1850_1958_years,CO2_observed_since_1959_years))
   
    
# save:
np.save('Output/to-pickle/CO2_observed_years.npy',CO2_observed_years)
np.save('Output/to-pickle/CO2_observed.npy',CO2_observed)
np.save('Output/to-pickle/CO2_monthly_observed_years.npy',CO2_monthly_observed_years)
np.save('Output/to-pickle/CO2_monthly_observed.npy',CO2_monthly_observed)

# now future RCP8.5 CO2 projections:

df26 = pd.read_table('../../../Data-for-teaching-staff/Greenhouse/RCP3PD_MIDYR_CONC.DAT',sep='      ',header=40,engine='python')
data_rcp_26 = df26.values
df45 = pd.read_table('../../../Data-for-teaching-staff/Greenhouse/RCP45_MIDYR_CONC.DAT',sep='      ',header=40,engine='python')
data_rcp_45 = df45.values
df6 = pd.read_table('../../../Data-for-teaching-staff/Greenhouse/RCP6_MIDYR_CONC.DAT',sep='      ',header=40,engine='python')
data_rcp_6 = df6.values
df85 = pd.read_table('../../../Data-for-teaching-staff/Greenhouse/RCP85_MIDYR_CONC.DAT',sep='      ',header=40,engine='python')
data_rcp_85 = df85.values

arg_start = np.argwhere(data_rcp_85[:,0] ==2000)[0][0]
arg_stop = np.argwhere(data_rcp_85[:,0] ==2100)[0][0]

CO2_rcp85_years = data_rcp_85[arg_start:arg_stop+1,0]
CO2_rcp26 = data_rcp_26[arg_start:arg_stop+1,3]
CO2_rcp45 = data_rcp_45[arg_start:arg_stop+1,3]
CO2_rcp6 = data_rcp_6[arg_start:arg_stop+1,3]
CO2_rcp85 = data_rcp_85[arg_start:arg_stop+1,3]

np.save('Output/to-pickle/CO2_rcp85_years.npy',CO2_rcp85_years)
np.save('Output/to-pickle/CO2_rcp26.npy',CO2_rcp26)
np.save('Output/to-pickle/CO2_rcp45.npy',CO2_rcp45)
np.save('Output/to-pickle/CO2_rcp6.npy',CO2_rcp6)
np.save('Output/to-pickle/CO2_rcp85.npy',CO2_rcp85)

# plot:
# plot:
fig = plt.figure(1,figsize=(5,3),dpi=300)
plt.plot(CO2_monthly_observed_years,CO2_monthly_observed,label="Observed",lw=2,color="b",zorder=10)
plt.plot(CO2_rcp85_years,CO2_rcp26,label="RCP2.6",color="g",zorder=1)
plt.plot(CO2_rcp85_years,CO2_rcp45,label="RCP4.5",color="k",zorder=1)
plt.plot(CO2_rcp85_years,CO2_rcp6,label="RCP6",color="c",zorder=1)
plt.plot(CO2_rcp85_years,CO2_rcp85,label="RCP8.5",color="r",zorder=1)
plt.xlabel("Year")
plt.ylabel("CO$_2$ (ppm)")
plt.legend()
plt.grid(lw=0.25)
plt.xlim(1850,2100)
plt.tight_layout()
plt.show()
fig.savefig("Output/greenhouse-CO2-timeseries-observed-and-RCPs.pdf")
