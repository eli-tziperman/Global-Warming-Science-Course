import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from numpy import loadtxt
from netCDF4 import Dataset
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy import config
from mpl_toolkits.axes_grid1 import make_axes_locatable
import glob, os, re


# read sea ice age for all years, and axes:
# -----------------------------------------
age_data_directory="../../../Data-for-teaching-staff/Sea-ice/age/"
pat = re.compile(r"iceage_nh_12\.5km_(\d{4})0101_\d{8}_v4\.1\.nc$")
years = sorted(
    int(m.group(1))
    for f in glob.glob(os.path.join(age_data_directory, "iceage_nh_12.5km_*_v4.1.nc"))
    if (m := pat.search(os.path.basename(f)))
)
first_year_age, last_year_age = years[0], years[-1]
print("Found age data for the year range:", first_year_age, last_year_age)
for year in range(first_year_age,last_year_age+1):
    print(year)
    age_data_file=age_data_directory+"iceage_nh_12.5km_"+repr(year)+"0101_"+repr(year)+"1231_v4.1.nc"

    ncfile = Dataset(age_data_file, 'r');
    sic_age_obs = np.asarray(ncfile.variables['age_of_sea_ice'][:])
    # save variables to be pickled: March sea ice age:
    filename_output="Output/age_npy/sic_age_obs"+repr(year)+".npy"
    np.save(filename_output,sic_age_obs[2,:,:])

sic_age_obs_lon = np.asarray(ncfile.variables['longitude'][:])
sic_age_obs_lat = np.asarray(ncfile.variables['latitude'][:])
np.save("Output/to-pickle/sic_age_obs_lon.npy",sic_age_obs_lon)
np.save("Output/to-pickle/sic_age_obs_lat.npy",sic_age_obs_lat)


# plot:
# -----
plt.figure(figsize=(6,6))
sic_age_obs=np.load("Output/age_npy/sic_age_obs1984.npy")
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0, globe=None))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
c=plt.pcolormesh(sic_age_obs_lon, sic_age_obs_lat, sic_age_obs[:,:]\
                 ,transform=ccrs.PlateCarree(), cmap='jet', vmin=0, vmax=10)
plt.xticks(np.arange(-60,0,20))
plt.yticks(np.arange(50,90,10))
plt.title('sea ice age '+repr(first_year_age));
plt.colorbar(c, shrink=0.7, pad=0.02)
plt.pause(1.0)

plt.clf()
plt.figure(figsize=(6,6))
sic_age_obs=np.load("Output/age_npy/sic_age_obs"+repr(last_year_age)+".npy")
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0, globe=None))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
c=plt.pcolormesh(sic_age_obs_lon, sic_age_obs_lat, sic_age_obs[:,:]\
    ,transform=ccrs.PlateCarree(), cmap='jet', vmin=0, vmax=10)
plt.xticks(np.arange(-60,0,20))
plt.yticks(np.arange(50,90,10))
plt.title('sea ice age '+repr(last_year_age));
plt.colorbar(c, shrink=0.7, pad=0.02)
plt.pause(1.0)

