#!/usr/bin/env python
import numpy as np
from numpy import linalg
import scipy as scipy
import matplotlib.pyplot as plt
import matplotlib
from netCDF4 import Dataset
# cortopy allows to plot data over maps in various spherical prjections"
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy import config
from mpl_toolkits.axes_grid1 import make_axes_locatable

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

filename_obs='../../../Data-for-teaching-staff/Acidification/Surface_pH_1770_2000.nc';
filename_rcp85='../../../Data-for-teaching-staff/Acidification/Surface_pH_2010_2100_RCP85.nc';
ncfile_obs = Dataset(filename_obs, 'r');
ncfile_rcp85 = Dataset(filename_rcp85, 'r');

longitude=np.asarray(ncfile_obs.variables['Longitude'][:]);
latitude=np.asarray(ncfile_obs.variables['Latitude'][:]);
pH_obs = np.asarray(ncfile_obs.variables['pH'][:]);
pH_rcp85 = np.asarray(ncfile_rcp85.variables['pH'][:]);
pH_obs_years=np.asarray(ncfile_obs.variables['Year'][:]);
pH_rcp85_years=np.asarray(ncfile_rcp85.variables['Year'][:]);

# produce a time series of global, yearly average pH:
dlon=longitude[0,1]-longitude[0,0]
dlat=latitude[1,0]-latitude[0,0]
#print("dlon,dlat=",dlon,dlat)
R=6700.0e3 # Earth radius

ocean_mask=pH_rcp85[0,0,:,:]*1.0
ocean_mask[~np.isnan(ocean_mask)]=1.0
ocean_mask[np.isnan(ocean_mask)]=0.0

delta_area=R**2*dlon*dlat*(np.pi/180)**2*np.cos(latitude*np.pi/180)*ocean_mask
total_area=np.nansum(delta_area,axis=(0,1))
pH_obs_global_decadal_mean=np.nansum(pH_obs*delta_area*ocean_mask,axis=(1,2,3))/total_area/12
pH_rcp85_global_decadal_mean=np.nansum(pH_rcp85*delta_area*ocean_mask,axis=(1,2,3))/total_area/12
#print("total area=",total_area/1.e12," million km^2")
#print("etimated total area:",0.71*(4*np.pi*R**2)/1.0e12)
#print("pH_obs_global_decadal_mean=",pH_obs_global_decadal_mean)
#print("pH_rcp85_global_decadal_mean=",pH_rcp85_global_decadal_mean)
#print(pH_rcp85_years,pH_obs_years)


# contour pH:
year=0
month=0
c=plt.contourf(longitude, latitude, pH_rcp85[year,month,:,:],20)
#c=plt.contourf(longitude, latitude, ocean_mask)
# draw the colorbar
clb=plt.colorbar(c, shrink=0.85, pad=0.02)
# add title/ labels:
plt.xlabel('Longitude')
plt.ylabel('Latitude')
clb.set_label('pH')
plt.title('pH, rcp85, year='+repr(int(pH_rcp85_years[year]))+", month="+repr(month+1))
plt.show()

# save three maps of pH at critical times:
pH_obs_1850=np.nanmean(pH_obs[8,:,:,:],axis=0)
pH_obs_2000=np.nanmean(pH_obs[-1,:,:,:],axis=0)
pH_rcp85_2100=np.nanmean(pH_rcp85[-1,:,:,:],axis=0)

# in global mean time series, keep only values starting 1850:
pH_obs_global_decadal_mean=pH_obs_global_decadal_mean[pH_obs_years>1849]
pH_obs_years=pH_obs_years[pH_obs_years>1849] # this must be the 2nd line!

# save variables to be pickled:
np.save("Output/to-pickle/pH_map_longitude.npy",longitude)
np.save("Output/to-pickle/pH_map_latitude.npy",latitude)
np.save("Output/to-pickle/pH_obs_1850_map.npy",pH_obs_1850)
np.save("Output/to-pickle/pH_obs_2000_map.npy",pH_obs_2000)
np.save("Output/to-pickle/pH_rcp85_2100_map.npy",pH_rcp85_2100)
np.save("Output/to-pickle/pH_obs_global_decadal_mean.npy",pH_obs_global_decadal_mean)
np.save("Output/to-pickle/pH_obs_global_decadal_mean_years.npy",pH_obs_years)
np.save("Output/to-pickle/pH_rcp85_global_decadal_mean.npy",pH_rcp85_global_decadal_mean)
np.save("Output/to-pickle/pH_rcp85_global_decadal_mean_years.npy",pH_rcp85_years)
