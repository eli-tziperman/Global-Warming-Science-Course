# read monthly AMOC from GFDL CMIP5 RCP8.5, save stream function
# averaged over first andlast decades, and save time series of max
# value.

import numpy as np
from numpy import linalg
import scipy as scipy
import matplotlib.pyplot as plt
import matplotlib
from netCDF4 import Dataset
from netCDF4 import chartostring
import glob
import pickle

def pickle_vars(fileName, env, *variables):
    d = dict([(x, env[x]) for v in variables for x in env if v is env[x]])
    with open(fileName, 'wb') as f:
        pickle.dump(d, f)

path_to_nc_files='../../../Data-for-teaching-staff/Ocean-circulation/msftyyz_Omon_GFDL-CM3_rcp85_r1i1p1_20*'
# get and sort netcdf file names from data folder:
filelist=glob.glob(path_to_nc_files)
filelist.sort()
N_files=len(filelist)
N_months=N_files*60 # 5 years in each file

# open pickle file:
ifile=0
imonth=0
for filename in filelist:
    # open monthly file:
    ncfile = Dataset(filename, 'r')

    # load data, keep in Sverdrup:
    AMOC = ncfile.variables['msftyyz'][:,3,:,:]/1.e9
    AMOC[AMOC>1.e19]=np.nan
    AMOC=np.asarray(AMOC)


    # add stream function and max value to appropriate arrays:
    if ifile==0:
        # read coordinates for depth and latitude:
        rcp85_depth = np.asarray(ncfile.variables['lev'][:])
        rcp85_latitude = np.asarray(ncfile.variables['rlat'][:])
        nmonths,nz,ny=AMOC.shape
        AMOC_streamfunction=np.zeros((N_months,nz,ny))
        rcp85_AMOC_timeseries=np.zeros(N_months)
        #print("sizes of array in each file: ",AMOC.shape)
        region = chartostring(ncfile.variables['region'][:])
        print("regions=",region,"\nreading region 3:",region[3])

    
    AMOC_streamfunction[imonth:imonth+60,:,:]=AMOC

    # get max AMOC stream function over specified depth and latituede ranges:
    XX1=AMOC[:,np.logical_and(rcp85_depth>500,rcp85_depth<2000),:]
    XX2=XX1[:,:,np.logical_and(rcp85_latitude>30,rcp85_latitude<70)]
    rcp85_AMOC_timeseries[imonth:imonth+60]=np.max(XX2,axis=(1,2))

    # update month and file counters:
    imonth=imonth+60
    ifile=ifile+1

# calculate first and last decade averages:
rcp85_AMOC_first_decade,=np.mean(AMOC_streamfunction[:120,:,:],axis=0),
rcp85_AMOC_last_decade,=np.mean(AMOC_streamfunction[-120:,:,:],axis=0),
levels=np.arange(-8,28,2)


# plot first and last decade stream functions:
plt.figure(figsize=(12,6))
plt.subplot(1,2,1)
plt.contourf(rcp85_latitude,rcp85_depth,rcp85_AMOC_first_decade,levels)
plt.gca().invert_yaxis()
plt.colorbar()
plt.title("AMOC first decade")
plt.xlim(-40,90)

plt.subplot(1,2,2)
plt.contourf(rcp85_latitude,rcp85_depth,rcp85_AMOC_last_decade,levels)
plt.gca().invert_yaxis()
plt.colorbar()
plt.title("AMOC, last decade")
plt.xlim(-40,90)
plt.tight_layout()
plt.show()

# plot max AMOC stream function time series:
plt.figure(figsize=(12,6))
rcp85_years=2006+np.arange(0,N_months,1)/12
plt.plot(rcp85_years,rcp85_AMOC_timeseries)
plt.xlabel("year")
plt.ylabel("Sv")
plt.title("max AMOC time series")
plt.show()

# save into file:
# ---------------
np.save("Output/to-pickle/rcp85_depth.npy",rcp85_depth)
np.save("Output/to-pickle/rcp85_latitude.npy",rcp85_latitude)
np.save("Output/to-pickle/rcp85_AMOC_first_decade.npy",rcp85_AMOC_first_decade)
np.save("Output/to-pickle/rcp85_AMOC_last_decade.npy",rcp85_AMOC_last_decade)
np.save("Output/to-pickle/rcp85_years.npy",rcp85_years)
np.save("Output/to-pickle/rcp85_AMOC_timeseries.npy",rcp85_AMOC_timeseries)
