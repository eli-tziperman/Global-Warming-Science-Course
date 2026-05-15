# download sea ice age data from NSIDC, save it for further processing
# as npy files and contour the first and last years of data.

import netrc,datetime
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import aiohttp,fsspec
import xarray as xr

# -----------------------
# Specify data location:
# -----------------------
BASE="https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0611_seaice_age_v4/data/"
FN="iceage_nh_12.5km_{y}0101_{y}1231_v4.1.nc"   # verified working (e.g. 1984)

# get userid and password from ~/.netrc and login:
a=netrc.netrc().authenticators("urs.earthdata.nasa.gov")
user,pw=a[0],a[2]
FS=fsspec.filesystem("https", client_kwargs={"auth": aiohttp.BasicAuth(user,pw)})

# -----------------------
# Find last year in data:
# -----------------------
def exists_year(y):
    url=BASE+FN.format(y=y)
    try:
        with FS.open(url,"rb") as f: f.read(1)
        return True
    except Exception:
        return False

first_year_age=1984
last_year_age=datetime.date.today().year+1
while last_year_age>=first_year_age and not exists_year(last_year_age):
    last_year_age-=1

print("Found age data for the year range:",first_year_age,last_year_age)


# ---------------------------------
# Loop over all years, save as npy:
# ---------------------------------
sic_age_obs_lon=None
for y in range(first_year_age,last_year_age+1):
    print(y)
    with FS.open(BASE+FN.format(y=y),"rb") as f:
        ds=xr.open_dataset(f,engine="h5netcdf")
        v=ds["age_of_sea_ice"]
        np.save(f"Output/age_npy/sic_age_obs{y}.npy", v.isel({v.dims[0]:2}).values)
        if sic_age_obs_lon is None:
            sic_age_obs_lon=(ds["longitude"] if "longitude" in ds else ds["lon"]).values
            sic_age_obs_lat=(ds["latitude"] if "latitude" in ds else ds["lat"]).values
        ds.close()

np.save("Output/to-pickle/sic_age_obs_lon.npy",sic_age_obs_lon)
np.save("Output/to-pickle/sic_age_obs_lat.npy",sic_age_obs_lat)

# --------------------------
# Plot first and last years:
# --------------------------
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
f = plt.gcf()  # f = figure(n) if you know the figure number
f.set_size_inches(5, 4)
f.savefig("Output/Figure-sea-ice-age-"+repr(first_year_age)+".pdf",format='pdf');


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
f = plt.gcf()  # f = figure(n) if you know the figure number
f.set_size_inches(5, 4)
f.savefig("Output/Figure-sea-ice-age-"+repr(last_year_age)+".pdf",format='pdf');
