import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from numpy import loadtxt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy import config
from mpl_toolkits.axes_grid1 import make_axes_locatable
import glob, os, re

# read sea ice thickness for two years, and axes:
# -----------------------------------------------
# pixel lon/ lat:
sic_thickness_obs_lon = loadtxt("Output/thickness_dat/sic_thickness_clon.dat",unpack=True);
sic_thickness_obs_lat = loadtxt("Output/thickness_dat/sic_thickness_clat.dat",unpack=True);
# pixel edge size on north and east edges:
sic_thickness_obs_HTN = loadtxt("Output/thickness_dat/sic_thickness_HTN.dat",unpack=True);
sic_thickness_obs_HTE = loadtxt("Output/thickness_dat/sic_thickness_HTE.dat",unpack=True);
sic_thickness_cell_area=sic_thickness_obs_HTE*sic_thickness_obs_HTN
mask = loadtxt("Output/thickness_dat/sic_thickness_mask.dat",unpack=True);
nx,ny=sic_thickness_obs_lat.shape
sic_thickness_obs=np.zeros((nx,ny,12))

thickness_data_directory="Output/thickness_dat/"
pat = re.compile(r"^heff(\d{4})\.dat$")

years = sorted(
    int(m.group(1))
    for f in glob.glob(os.path.join(thickness_data_directory, "heff*.dat"))
    if (m := pat.match(os.path.basename(f)))
)

first_year_thickness, last_year_thickness = years[0], years[-1]
print("Found thickness data for the year range "
      , first_year_thickness, last_year_thickness)

for year in range(first_year_thickness,last_year_thickness+1):
    print(year)
    for month in range(0,12):
        filename_input=thickness_data_directory+"heff"+repr(year)+".dat"
        sic_thickness_obs_tmp = loadtxt(filename_input,unpack=True);
        sic_thickness_obs[:,:,month]=sic_thickness_obs_tmp[:,month*120:(month+1)*120]#*mask

    # save variables to be pickled:
    filename_output="Output/thickness_npy/sic_thickness_obs"+repr(year)+".npy"
    np.save(filename_output,sic_thickness_obs)


    np.save("Output/to-pickle/sic_thickness_obs_lon.npy",sic_thickness_obs_lon)
    np.save("Output/to-pickle/sic_thickness_obs_lat.npy",sic_thickness_obs_lat)
    np.save("Output/to-pickle/sic_thickness_obs_cell_area.npy",sic_thickness_cell_area)

    
# plot:
# -----
plt.figure(figsize=(6,6))
sic_thickness_obs_first_year=np.load("Output/thickness_npy/sic_thickness_obs"
                                     +repr(first_year_thickness)+".npy")
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0, globe=None))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
c=plt.pcolormesh(sic_thickness_obs_lon, sic_thickness_obs_lat
                 , sic_thickness_obs_first_year[:,:,3] \
                 ,transform=ccrs.PlateCarree(), cmap='jet',shading='auto')
plt.xticks(np.arange(-60,0,20))
plt.yticks(np.arange(50,90,10))
plt.title('sea ice sic_thickness_obs '+repr(first_year_thickness));
plt.colorbar(c, shrink=0.7, pad=0.02)
plt.pause(2)

plt.clf()
plt.figure(figsize=(6,6))
sic_thickness_obs_last_year=np.load("Output/thickness_npy/sic_thickness_obs"
                              +repr(last_year_thickness)+".npy")
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0, globe=None))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
c=plt.pcolormesh(sic_thickness_obs_lon, sic_thickness_obs_lat
                 , sic_thickness_obs_last_year[:,:,3]\
                 , transform=ccrs.PlateCarree(), cmap='jet',shading='auto')
plt.xticks(np.arange(-60,0,20))
plt.yticks(np.arange(50,90,10))
plt.title('sea ice sic_thickness_obs '+repr(last_year_thickness));
plt.colorbar(c, shrink=0.7, pad=0.02)
plt.pause(2)

