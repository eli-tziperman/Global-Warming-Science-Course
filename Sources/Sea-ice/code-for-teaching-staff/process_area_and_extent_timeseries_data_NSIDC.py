# Read monthly data files for sea ice area and extent from NSIDC, save as time series.
# Eli

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# read sea ice area/extent data:
# -----------------------------------------------
data_dir="../../../Data-for-teaching-staff/Sea-ice/area-extent-indices/"

area_S=[]
area_N=[]
extent_S=[]
extent_N=[]
years_S=[]
months_S=[]
years_N=[]
months_N=[]
for month in range(1,13):
    filename_S="S_%02d_extent_v3.0.csv" % month
    filename_N="N_%02d_extent_v3.0.csv" % month
    dataset_S = pd.read_csv(data_dir+filename_S,sep=',',na_values='NaN'
                          ,comment='#',skipinitialspace=True\
                          ,skip_blank_lines=True,header=0)
    dataset_N = pd.read_csv(data_dir+filename_N,sep=',',na_values='NaN'
                          ,comment='#',skipinitialspace=True\
                          ,skip_blank_lines=True,header=0)
    data_S=np.asarray(dataset_S.iloc[:, :].values)
    data_N=np.asarray(dataset_N.iloc[:, :].values)
    years_S.extend(data_S[:,0])
    months_S.extend(data_S[:,1])
    years_N.extend(data_N[:,0])
    months_N.extend(data_N[:,1])
    extent_S.extend(data_S[:,4])
    area_S.extend(data_S[:,5])
    extent_N.extend(data_N[:,4])
    area_N.extend(data_N[:,5])
    header_S = dataset_S.iloc[:, :].columns
    header_N = dataset_N.iloc[:, :].columns
    #print(header,area,extent)

years_S=1*np.asarray(years_S,dtype=np.int64)
months_S=1.0*np.asarray(months_S)
years_N=1*np.asarray(years_N,dtype=np.int64)
months_N=1.0*np.asarray(months_N)
extent_S=1.0*np.asarray(extent_S)
area_S=1.0*np.asarray(area_S)
extent_N=1.0*np.asarray(extent_N)
area_N=1.0*np.asarray(area_N)
start_year_S=np.min(years_S)
end_year_S=np.max(years_S)
start_year_N=np.min(years_N)
end_year_N=np.max(years_N)


time_S=[]
time_N=[]
extent_timeseries_S=[]
area_timeseries_S=[]
extent_timeseries_N=[]
area_timeseries_N=[]
for i in range(len(years_S)):
    time_S.append(years_S[i]+(months_S[i]-0.5)/12.0)
    extent_timeseries_S.append(extent_S[i])
    area_timeseries_S.append(area_S[i])

for i in range(len(years_N)):
    time_N.append(years_N[i]+(months_N[i]-0.5)/12.0)
    extent_timeseries_N.append(extent_N[i])
    area_timeseries_N.append(area_N[i])

time_S=1.0*np.asarray(time_S)
time_N=1.0*np.asarray(time_N)
area_timeseries_S=1.0*np.asarray(area_timeseries_S)
extent_timeseries_S=1.0*np.asarray(extent_timeseries_S)
area_timeseries_N=1.0*np.asarray(area_timeseries_N)
extent_timeseries_N=1.0*np.asarray(extent_timeseries_N)

# Interpolate missing data where where value is -9999:
# [Interpolation is applied to data from a given month, so we are
# interpolating missing december values from other december values.]

def my_interpolate(a):
    for i in range(0,len(a)):
        if a[i]<-9998:
            a[i]=(a[i-1]+a[i+1])/2.0
    return a

area_timeseries_S  =1.0*my_interpolate(area_timeseries_S)
extent_timeseries_S=1.0*my_interpolate(extent_timeseries_S)
area_timeseries_N  =1.0*my_interpolate(area_timeseries_N)
extent_timeseries_N=1.0*my_interpolate(extent_timeseries_N)


# sort data by time:
time_indices_S = time_S.argsort()
time_indices_N = time_N.argsort()
area_timeseries_S = 1.0*area_timeseries_S[time_indices_S[:]]
extent_timeseries_S = 1.0*extent_timeseries_S[time_indices_S[:]]
area_timeseries_N = 1.0*area_timeseries_N[time_indices_N[:]]
extent_timeseries_N = 1.0*extent_timeseries_N[time_indices_N[:]]
time_S = 1.0*time_S[time_indices_S[:]]
time_N = 1.0*time_N[time_indices_N[:]]

print("First and last times for Arctic: %g, %g; Antarctic: %g, %g;"
      % (time_N[0], time_N[-1], time_S[0], time_S[-1]) )

# plot:
# -----

# seasonal cycle at both hemispheres:
plt.figure(1,figsize=(18,6))
plt.subplot(1,2,1)
plt.plot(time_S,area_timeseries_S,'-xr',label="area")
plt.plot(time_S,extent_timeseries_S,'-xb',label="extent")
plt.title("South")
plt.legend()
plt.xlabel("year")

plt.subplot(1,2,2)
plt.plot(time_N,area_timeseries_N,'-xr',label="area")
plt.plot(time_N,extent_timeseries_N,'-xb',label="extent")
plt.title("North")
plt.xlabel("year")

plt.tight_layout()
plt.pause(1.0)


# minimum sea ice in NH:
line_fit_pars = np.polyfit(time_N[8::12],area_timeseries_N[8::12], 1)
linefit=line_fit_pars[0]*time_N[8::12]+line_fit_pars[1]
plt.figure(2,figsize=(6,4))
plt.plot(time_N[8::12],area_timeseries_N[8::12],'-or',label="Observed")
plt.plot(time_N[8::12],linefit,'b',label="Linear fit")
plt.title("Arctic September sea ice area")
plt.xlabel("year")
plt.ylabel("$10^6$ km$^2$")
plt.grid(lw=0.25)
plt.legend()
plt.tight_layout()
f = plt.gcf()  # f = figure(n) if you know the figure number
f.savefig("Output/Figure-September-Arctic-sea-ice-area.pdf",format='pdf');
plt.pause(1.0)


# save variables to be pickled:
# [starting from Jan 1979, ignoring two final months of 1978 for simplicity]
if 1:
    np.save("Output/to-pickle/sic_area_obs_timeseries_Antarctica.npy",area_timeseries_S[2:])
    np.save("Output/to-pickle/sic_area_obs_timeseries_time_Antarctica.npy",time_S[2:])
    np.save("Output/to-pickle/sic_extent_obs_timeseries_Antarctica.npy",extent_timeseries_S[2:])
    np.save("Output/to-pickle/sic_extent_obs_timeseries_time_Antarctica.npy",time_S[2:])
    np.save("Output/to-pickle/sic_area_obs_timeseries_Arctic.npy",area_timeseries_N[2:])
    np.save("Output/to-pickle/sic_area_obs_timeseries_time_Arctic.npy",time_N[2:])
    np.save("Output/to-pickle/sic_extent_obs_timeseries_Arctic.npy",extent_timeseries_N[2:])
    np.save("Output/to-pickle/sic_extent_obs_timeseries_time_Arctic.npy",time_N[2:])
