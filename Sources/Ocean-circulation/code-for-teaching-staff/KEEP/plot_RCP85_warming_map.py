# plot SST (T_s?) warming to see if a signal of the ocean circulation collapse can be seen

import numpy as np
from netCDF4 import Dataset
import math
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
from cartopy.util import add_cyclic_point
import matplotlib.ticker as mticker
from scipy import interpolate

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

# open files:
file_2006='../../../Data-for-teaching-staff/Ocean-circulation/SST-RCP8.5/tos_Omon_GFDL-ESM2M_rcp85_r1i1p1_200601-201012-avg.nc'
file_2100='../../../Data-for-teaching-staff/Ocean-circulation/SST-RCP8.5/tos_Omon_GFDL-ESM2M_rcp85_r1i1p1_209601-210012-avg.nc'
nc_2006 = Dataset(file_2006, 'r');
nc_2100 = Dataset(file_2100, 'r');

# get data:
lat = nc_2100.variables['lat'][:].T
lon = nc_2100.variables['lon'][:].T
TOS_2006=nc_2006.variables['tos'][:].T
TOS_2100=nc_2100.variables['tos'][:].T
TOS_2006[TOS_2006>1.e5]=np.nan
TOS_2100[TOS_2100>1.e5]=np.nan
DATA=np.asarray(TOS_2100-TOS_2006)

# interpolate to a regular lon/lat grid using "nearest" method; that's
# the only way I could get rid of the gap in longitude:
lon = ((lon + 180) % 360) - 180
x = np.arange(-179.5, 180.5, 1)
y = np.arange(-90, 91, 1)
mylon, mylat = np.meshgrid(x, y)

x=lon.flatten()
y=lat.flatten()
d=DATA.flatten()
myDATA=interpolate.griddata((x, y), d, (mylon,mylat), method='nearest')
lon=mylon;lat=mylat;DATA=myDATA


# -------------------------
# Plot
# -------------------------
fig=plt.figure(figsize=(4,4),dpi=200)
ax=fig.add_subplot(1,1,1, projection=ccrs.Orthographic(-45, 45))

# add coastlines:
ax.stock_img()
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.COASTLINE)

# Draw the contours:
delta=1; levels=np.arange(-8,8+delta,delta)
plt.contourf(lon,lat,DATA,levels=levels,cmap="bwr",transform=ccrs.PlateCarree())

# Add a color bar
cb=plt.colorbar(ax=ax, shrink=0.5, pad=0.02, ticks=np.arange(-8,10,2))
cb.set_label("°C")

# Add the gridlines
gl=ax.gridlines(color="grey",linewidth=0.25)
gl.ylocator = mticker.FixedLocator(range(-80,100,20))

plt.tight_layout()
plt.show()
fig.savefig("Output/ocean-circulation-MOC-collapse-SST-warming-RCP85.pdf")
