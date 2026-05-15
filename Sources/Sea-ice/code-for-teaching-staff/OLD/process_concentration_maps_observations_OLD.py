# read sea ice concentration maps from observations, create a pickle
# file for september sea ice.
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from numpy import loadtxt
from netCDF4 import Dataset
import glob
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy import config
from mpl_toolkits.axes_grid1 import make_axes_locatable


# get sorted names of data files:
# --------------------------------
data_file="../../../Data-for-teaching-staff/Sea-ice/" \
    +"concentration_maps/G10010_sibt1850_v2.0.nc"

# create variable to hold september sea ice for all years, use the
# first month to get the dimensions:
ncfile = Dataset(data_file, 'r');
# multiply by 1.0 to convert from integer to real:
sic = np.asarray(ncfile.variables['seaice_conc'][:])*1.0
# points with concentration==120 indicate land, set them to NaN:
sic[np.isnan(sic)]=130 # first set nans to 130
sic[1.0*sic>119.0]=np.nan # now set 120 and 130 values to nan
N_months,ny,nx=sic.shape
sic_concentration_obs_sept=sic[list(range(8,N_months,12)),:,:]
sic_concentration_obs_years=1850+np.arange(0,int(N_months/12))
sic_concentration_obs_lon=np.asarray(ncfile.variables['longitude'][:])
sic_concentration_obs_lat=np.asarray(ncfile.variables['latitude'][:])


# keep only 1979 and later, when data are from sattelites and
# therefore more reliable:
sic_concentration_obs_sept=sic_concentration_obs_sept[sic_concentration_obs_years>=1979,:,:]
sic_concentration_obs_years=sic_concentration_obs_years[sic_concentration_obs_years>=1979]


# plot the 1st month to verify that all is well:
# ----------------------------------------------
plt.figure(1,figsize=(6,6))
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0, globe=None))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
year=10
c=plt.pcolormesh(sic_concentration_obs_lon, sic_concentration_obs_lat\
                 , sic_concentration_obs_sept[year,:,:]\
                 ,transform=ccrs.PlateCarree(), cmap='jet')
plt.title('Sept sea ice concentration (%), year: '+repr(sic_concentration_obs_years[year]));
plt.colorbar(c, shrink=0.85, pad=0.02)
plt.pause(2.0)

# save variables to be pickled:
np.save("Output/to-pickle/sic_concentration_obs_sept.npy",sic_concentration_obs_sept)
np.save("Output/to-pickle/sic_concentration_obs_lon.npy",sic_concentration_obs_lon)
np.save("Output/to-pickle/sic_concentration_obs_lat.npy",sic_concentration_obs_lat)
np.save("Output/to-pickle/sic_concentration_obs_years.npy",sic_concentration_obs_years)
