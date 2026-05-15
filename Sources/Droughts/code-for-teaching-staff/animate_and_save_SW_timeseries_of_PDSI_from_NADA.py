"""A script to create a time series of averaged PDSI for
SouthWest US and an animation for North America from NADA data set.

Input: link to NADA PDSI reconstruction .nc file:
     https://www.ncei.noaa.gov/pub/data/paleo/drought/LBDA2010/nada_hd2_cl.nc)

Outputs:
  - Frames: ./Output/frames/frame-00000.png, ...
  - Timeseries npy file and plot.

Yonathan Vardi 2019-22-07, modified by Eli, 202510 to read from the
cloud and use xarray.
"""

########################################################################
# path/link to the netcdf file:
NADA_PATH = "../../../Data-for-teaching-staff/Droughts/nada_hd2_cl.nc"
NADA_LINK = "https://www.ncei.noaa.gov/pub/data/paleo/drought/LBDA2010/nada_hd2_cl.nc"
########################################################################

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import fsspec
from fsspec.core import open_local

def animate_PDSI():
    # draw animation frames and calculate average pdsi over south west US:
    fig = plt.figure(1)
    ax = plt.axes(projection=ccrs.PlateCarree())
    cmap = mpl.cm.BrBG
    norm = mpl.colors.Normalize(vmin=-4, vmax=4)
    cb_setter_array = np.asarray([np.arange(-4,5,1), np.arange(-4,5,1)])
    cb_setter = plt.contourf(cb_setter_array, 99, norm=norm, cmap=cmap)
    clb = fig.colorbar(cb_setter, ax=ax,ticks=[-4, -3, -2, -1, 0, 1, 2, 3, 4])
    clb.set_label('PDSI')

    pdsi=ds["pdsi"].transpose("lat", "lon", "time").values
    
    for i in range(len(pdsi[0,0,:])):
        if np.round(i/10)*10==i:
            print("%d,\t %d%%" % (i, np.floor(100*i/len(pdsi[0,0,:]))), end="\r")

        ax.clear()
        # draw map frames:
        fld = pdsi[:,:,i]
        ax.set_extent([np.min(lon), np.max(lon), np.min(lat), np.max(lat)],
                      crs=ccrs.PlateCarree())
        #ax.set_extent([-140, -50, 20, 80], crs=ccrs.PlateCarree())
        m = ax.pcolormesh(lon, lat, fld, transform=ccrs.PlateCarree(),
                          cmap=cmap, norm=norm, shading="auto")
        # coastlines:
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.7)
        ax.add_patch(Rectangle((lonmin, latmin), lonmax-lonmin, latmax-latmin,
                fill=None, alpha=1, ls="--"))
        ax.set_title("Palmer Drought Severity Index "+str(time[i])+" CE")
        plt.savefig("./Output/frames/frame-" + str(i).rjust(5, '0') + ".png")

    return PDSI_timeseries


########################################################################
## Main Program:
########################################################################

print("opening remote NADA data file:")
http_url = "simplecache::" + NADA_LINK
of = open_local(http_url)
ds = xr.open_dataset(of, engine="netcdf4")
#ds = xr.open_dataset(NADA_PATH)

pdsi = ds["pdsi"]
lat = ds["lat"].values[:]
lon = ds["lon"].values[:]
time = ds["time"].values[:]
print("done.")

print("Masking values")
pdsi.values[pdsi.values<-99]=np.nan

plt.figure(3)
flat = pdsi.stack(sample=('time','lat','lon'))   # 1D along 'sample'
flat = flat.where(np.isfinite(flat), drop=True)
ax = flat.plot.hist(bins=100)
plt.ylabel("# occurences")
plt.show(block=False)

plt.ioff()
os.makedirs("Output/frames", exist_ok=True)

# calculate an area-mean PDSI time series over the southwest:
# lat/lon of a box to draw around the South West US: 
lonmin, lonmax, latmin, latmax = -125, -105, 32, 41
print("Area-averaged time series...")
# select SW US sub-area for averaging:
sub = ds.sel(lon=slice(lonmin, lonmax), lat=slice(latmin, latmax))
weights = np.cos(np.deg2rad(sub["lat"]))
w = weights / weights.mean()
pdsi_sub = sub["pdsi"]
pdsi_sub.values[pdsi_sub.values<-99]=np.nan
# average:
#PDSI_timeseries = pdsi_sub.mean(dim=("lat", "lon"))
PDSI_timeseries = pdsi_sub.weighted(w).mean(dim=("lat", "lon"))
np.save("Output/PDSI_timeseries.npy", (np.asarray(time),PDSI_timeseries))

# animate:
print("Preparing PDSI animation...")
PDSI_timeseries=animate_PDSI()

print("Done. Frames saved to Output/frames/, to create the animation:")
print("cd Output/frames; ffmpeg -r 20 -f image2 -s 1920x1080 -i frame-%05d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p pdsi.mp4")

# plot PDSI time series averaged over SW US:
plt.figure(2, figsize=(15,5))
plt.plot(time,PDSI_timeseries,lw=0.5,color="red")
plt.plot(time,PDSI_timeseries*0-3,lw=0.25,ls="--",color="black")
plt.xlabel("year")
plt.ylabel("PDSI")
plt.title("PDSI averaged over South West US")
plt.savefig("Output/Figures/droughts-averaged_SouthWest-US-PDSI-timeseries.pdf",format='pdf');
plt.show()
