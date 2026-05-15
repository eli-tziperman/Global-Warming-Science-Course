# Calculate composite atmospheric jet for El Nino and La Nina,
# for looking at the effects on wind shear that can affect the
# hurricane season in the North Atlantic by downloading and using ERA5
# reanalysis.

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from netCDF4 import num2date
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from datetime import datetime
import matplotlib.patches as mpatches
import subprocess
import os
import cdsapi

# --- ERA5 download helper (replaces reading pre-downloaded local NetCDF files) ---
def _ensure_era5_monthly_files_1deg(out_dir):
    """Download ERA5 monthly means (1°x1°) needed by this notebook if
    not already present:
      - UV200.nc & UV850.nc : u,v at 200 hPa and at 850 hPa
      - SST.nc 
    """
    uv200_path = os.path.join(out_dir, "UV200.nc")
    uv850_path = os.path.join(out_dir, "UV850.nc")
    sst_path   = os.path.join(out_dir, "SST.nc")

    def _normalize_time_var_to_time(nc_path):
        ds = Dataset(nc_path)
        ds.close()

    # normalize the time coordinate:
    if all(os.path.exists(p) and os.path.getsize(p) > 0 for p in [uv200_path, uv850_path, sst_path]):
        for p in [uv200_path, uv850_path, sst_path]:
            _normalize_time_var_to_time(p)
        return out_dir + ("" if out_dir.endswith(os.sep) else os.sep)

    c = cdsapi.Client()

    years  = [str(y) for y in range(1979, 2025)]
    months = [f"{m:02d}" for m in range(1, 13)]
    time   = ["00:00"]

    # Pressure-level monthly means: U/V at 200 hPa
    if not (os.path.exists(uv200_path) and os.path.getsize(uv200_path) > 0):
        c.retrieve(
            "reanalysis-era5-pressure-levels-monthly-means",
            {
                "product_type": "monthly_averaged_reanalysis",
                "variable": ["u_component_of_wind", "v_component_of_wind"],
                "pressure_level": "200",
                "year": years,
                "month": months,
                "time": time,
                "grid": [1.0, 1.0],
                "format": "netcdf",
            },
            uv200_path,
        )
        _normalize_time_var_to_time(uv200_path)

    # Pressure-level monthly means: U/V at 850 hPa
    if not (os.path.exists(uv850_path) and os.path.getsize(uv850_path) > 0):
        c.retrieve(
            "reanalysis-era5-pressure-levels-monthly-means",
            {
                "product_type": "monthly_averaged_reanalysis",
                "variable": ["u_component_of_wind", "v_component_of_wind"],
                "pressure_level": "850",
                "year": years,
                "month": months,
                "time": time,
                "grid": [1.0, 1.0],
                "format": "netcdf",
            },
            uv850_path,
        )
        _normalize_time_var_to_time(uv850_path)

    # Single-level monthly means: SST
    if not (os.path.exists(sst_path) and os.path.getsize(sst_path) > 0):
        c.retrieve(
            "reanalysis-era5-single-levels-monthly-means",
            {
                "product_type": "monthly_averaged_reanalysis",
                "variable": "sea_surface_temperature",
                "year": years,
                "month": months,
                "time": time,
                "grid": [1.0, 1.0],
                "format": "netcdf",
            },
            sst_path,
        )
        _normalize_time_var_to_time(sst_path)

    # Also normalize in case files already existed from previous downloads
    for p in [uv200_path, uv850_path, sst_path]:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            _normalize_time_var_to_time(p)

    return os.path.join(out_dir, "")



# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'
plt.rcParams['font.size'] = 9

print("done.")

# read atmospheric grid information:
era5_data_dir = _ensure_era5_monthly_files_1deg("/Users/eli/Downloads/")
data_dir=era5_data_dir
file="UV200.nc"
ncfile = Dataset(data_dir+file, 'r');
lat = ncfile.variables['latitude'][:]
lon = ncfile.variables['longitude'][:]
times=ncfile.variables['valid_time'][:]

# read ocean grid information:
file="SST.nc"
ncfile_ocean = Dataset(data_dir+file, 'r');
lat_ocean = ncfile_ocean.variables['latitude'][:]
lon_ocean = ncfile_ocean.variables['longitude'][:]

# open SST file:
file="SST.nc"
ncfile= Dataset(data_dir+file, 'r');
SST= ncfile.variables['sst']

# open U,V files:
file="UV200.nc"
ncfile= Dataset(data_dir+file, 'r');
U200= ncfile.variables['u']
V200 = ncfile.variables['v']
data_dir=era5_data_dir
file="UV850.nc"
ncfile= Dataset(data_dir+file, 'r');
U850= ncfile.variables['u']
V850 = ncfile.variables['v']

# get grid/ time limits:
Nt,Nz,Ny,Nx=U200.shape

    
# calculate dates and month for each timestep using the NetCDF time metadata
t = ncfile.variables['valid_time']
dates = num2date(times, units=t.units, calendar=t.calendar)

# matplotlib can't plot cftime objects; convert to plain datetime:
dates = [datetime(d.year, d.month, d.day, d.hour, d.minute, int(d.second)) for d in dates]

months = np.array([d.month for d in dates])
print("calculated months time series.")

# initialize monthly climatoloigy arrays:
U200_climatology=np.zeros((12,Ny,Nx))
V200_climatology=np.zeros((12,Ny,Nx))
U850_climatology=np.zeros((12,Ny,Nx))
V850_climatology=np.zeros((12,Ny,Nx))
SST_climatology=np.zeros((12,Ny,Nx))

print("dimensions of U200,V200:",U200.shape)
print("dimensions of SST:",SST.shape)
print("first time:",dates[0],",last time:",dates[-1])

# plot quiver for first time in data, just for verification:
projection=ccrs.PlateCarree(central_longitude=0.0)
fig,axes=plt.subplots(1,1,figsize=(5,3),dpi=200,subplot_kw={'projection': projection})

# U,V:
# ----------------
U=U200[0,0,:,:]
V=V200[0,0,:,:]
SST1=SST[0,:,:]-273.15
axes.set_extent([-170, 10, -20, 60], crs=ccrs.PlateCarree())
axes.coastlines(resolution='110m',linewidth=0.5)
axes.stock_img()
axes.gridlines(linewidth=0.25)
plt.set_cmap('viridis')
levels=np.arange(0,6.3,0.3)
c=axes.pcolormesh(lon_ocean,lat_ocean, SST1[:,:])#,levels=levels)
s=4
axes.quiver(lon[::s], lat[::s], U[::s,::s], V[::s,::s],scale=1000\
            ,width=0.001,headwidth=10,headlength=10)
clb=plt.colorbar(c, pad=0.02, shrink=0.6, ax=axes)
clb.set_label('C')
axes.set_title('SST, (U,V)')

# finalize and show plot:
#plt.subplots_adjust(top=0.92, bottom=0.08, left=0.01, right=0.95, hspace=0.15,wspace=-0.4)
plt.pause(1);

print("done")


# define some functions to be able to process all files efficiently
# without running into memory problems:

def calculate_NINO34_timeseries():
    """ calculate a monthly time series of NINO3.4."""
    print("calculate_NINO34_timeseries... ",end="")
    # read data:
    data_dir=era5_data_dir
    file="SST.nc"
    ncfile= Dataset(data_dir+file, 'r');
    SST= ncfile.variables['sst']
    NINO34_timeseries=np.zeros(len(times))
    ilat=np.logical_and(lat<=5,lat>=-5)
    ilon=np.logical_and(lon<=360-120,lon>=360-170)
    NINO34_timeseries=np.nanmean(SST[:,ilat,ilon],axis=(1,2))

    # now remove monthly climatology from the NINO3 time series:
    NINO34_monthly_climatology=np.zeros(12)
    for m in range(12):
        NINO34_monthly_climatology[m]=np.mean(NINO34_timeseries[m::12])
        NINO34_timeseries[m::12]= \
           NINO34_timeseries[m::12]-NINO34_monthly_climatology[m]

    print(" done.")
    return NINO34_timeseries


def calculate_composite(variable,mask_timeseries,remove_monthly_climatology,monthly_climatology):
    # ERA5 pressure-level variables often come as (time, level, lat, lon),
    # while SST comes as (time, lat, lon). The original script assumes a
    # dummy level dimension; keep behavior but support both shapes.
    if getattr(variable, "ndim", None) == 4:
        def _slice(t):
            return variable[t,0,:,:]
    elif getattr(variable, "ndim", None) == 3:
        def _slice(t):
            return variable[t,:,:]
    else:
        raise ValueError(f"Unexpected number of dimensions for variable: {getattr(variable,'ndim',None)}")

    first_time_read=True
    iavg=0
    for t in range(len(times)):
        #print(t,",",end="")
        # read data:
        if not np.isnan(mask_timeseries[t]):
            if first_time_read:
                first_time_read=False
                variable_avg=1.0*_slice(t)
            else:
                variable_avg=variable_avg+_slice(t)
            if remove_monthly_climatology:
                variable_avg=variable_avg-monthly_climatology[int(months[t])-1,:,:]

            iavg=iavg+1

    if iavg>0:
        variable_avg=variable_avg/iavg
        variable_avg[variable_avg.mask]=np.nan
    else:
        print("\n\n\n*** error: no times to composite over.\n\n\n")
    #print(" done.")
    
    return variable_avg

print("function defenitions updated.")

NINO34_timeseries=calculate_NINO34_timeseries()
NINO34_timeseries=NINO34_timeseries[0:len(dates)]
    
mean=np.mean(NINO34_timeseries)
std=np.std(NINO34_timeseries)
print("nino3.4 mean, std=",mean,std)
ElNino_threshold=mean+std*1.5
LaNina_threshold=mean-std*1.5

# calculate El Nino/La Nina masks:
ElNino_mask_timeseries=NINO34_timeseries*0+1.0
ElNino_mask_timeseries[NINO34_timeseries<ElNino_threshold]=np.nan
num_ElNino_months=np.nansum(ElNino_mask_timeseries)
LaNina_mask_timeseries=NINO34_timeseries*0+1.0
LaNina_mask_timeseries[NINO34_timeseries>LaNina_threshold]=np.nan
num_LaNina_months=np.nansum(LaNina_mask_timeseries)
print("ElNino_threshold=",ElNino_threshold, ", number of ElNino months=",num_ElNino_months
      ,"=",100*num_ElNino_months/len(NINO34_timeseries),"%");
print("LaNina_threshold=",LaNina_threshold, ", number of LaNina months=",num_LaNina_months
      ,"=",100*num_LaNina_months/len(NINO34_timeseries),"%");

fig=plt.figure(dpi=300,figsize=(6,2.5))
plt.clf()
years=np.arange(len(NINO34_timeseries))/12
plt.plot(dates,NINO34_timeseries,lw=0.5,label="NINO3.4")
plt.plot(dates,ElNino_mask_timeseries*0+ElNino_threshold,".",color="r",markersize=0.75,label="El Nino")
plt.plot(dates,LaNina_mask_timeseries*0+LaNina_threshold,".",color="b",markersize=0.75,label="La Nina")
plt.xlabel("years")
plt.ylabel("Nino 3.4 (C)")
plt.legend(ncol=3)
plt.grid(lw=0.25);
plt.tight_layout()
plt.pause(1);

# calculate monthly climatologies:
print("Calculating monthly climatologies...")
remove_monthly_climatology=False
for m in range(0,12):
    climatology_mask_timeseries=np.zeros(ElNino_mask_timeseries.shape)*np.nan
    climatology_mask_timeseries[m::12]=1
    monthly_climatology=np.nan
    SST_climatology[m,:,:] =calculate_composite(SST,climatology_mask_timeseries,remove_monthly_climatology,monthly_climatology)
print("Done calculating monthly climatologies.")

# calculate composites for El Nina and La Nina:
print("Calculating El Nino/ La Nina composites...")
U200_composite_ElNino   =calculate_composite(U200  ,ElNino_mask_timeseries,remove_monthly_climatology,monthly_climatology)
V200_composite_ElNino   =calculate_composite(V200  ,ElNino_mask_timeseries,remove_monthly_climatology,monthly_climatology)
U200_composite_LaNina   =calculate_composite(U200  ,LaNina_mask_timeseries,remove_monthly_climatology,monthly_climatology)
V200_composite_LaNina   =calculate_composite(V200  ,LaNina_mask_timeseries,remove_monthly_climatology,monthly_climatology)
U850_composite_ElNino   =calculate_composite(U850  ,ElNino_mask_timeseries,remove_monthly_climatology,monthly_climatology)
V850_composite_ElNino   =calculate_composite(V850  ,ElNino_mask_timeseries,remove_monthly_climatology,monthly_climatology)
U850_composite_LaNina   =calculate_composite(U850  ,LaNina_mask_timeseries,remove_monthly_climatology,monthly_climatology)
V850_composite_LaNina   =calculate_composite(V850  ,LaNina_mask_timeseries,remove_monthly_climatology,monthly_climatology)
remove_monthly_climatology=True
SST_composite_ElNino =calculate_composite(SST,ElNino_mask_timeseries,remove_monthly_climatology,SST_climatology)
SST_composite_LaNina =calculate_composite(SST,LaNina_mask_timeseries,remove_monthly_climatology,SST_climatology)
print("Done calculating El Nino/ La Nina composites.")
    
# %%
# draw the climatologies and composites:

# prepare wind shear to be plotted following Wind shear is plotted 
# by Zhu-Saravanan-Chang-2012:influence
U_EN=1.0*(U200_composite_ElNino-U850_composite_ElNino)
V_EN=1.0*(V200_composite_ElNino-V850_composite_ElNino)
U_LN=1.0*(U200_composite_LaNina-U850_composite_LaNina)
V_LN=1.0*(V200_composite_LaNina-V850_composite_LaNina)

shear_magnitude_EN=np.sqrt(U_EN**2+V_EN**2)
shear_magnitude_LN=np.sqrt(U_LN**2+V_LN**2)


# land mask:
mask=np.zeros(SST_composite_ElNino.shape)+1
mask[np.isnan(SST_composite_ElNino)]=np.nan

# initialize figure:
projection=ccrs.PlateCarree(central_longitude=0.0);
fig=plt.figure(figsize=(5,3.5));
grid = plt.GridSpec(2, 2)#, wspace=0.4, hspace=0.3)


# El Nino:
# --------
axes=fig.add_subplot(2,2,1, projection=ccrs.PlateCarree(0))
axes.set_extent([-170, 10, -20.01, 60.01], crs=ccrs.PlateCarree(0))
axes.coastlines(resolution='110m',lw=0.3)
axes.stock_img()
plt.set_cmap('bwr')
DATA=1.0*SST_composite_ElNino[:,:]
c=axes.pcolormesh(lon,lat, DATA[:,:],vmin=-3,vmax=3,shading='auto')
clb=plt.colorbar(c, pad=0.02, shrink=0.55, ax=axes)
clb.set_label('°C')
s=4
axes.quiver(lon[::s], lat[::s], U_EN[::s,::s], V_EN[::s,::s],scale=400\
            ,width=0.001,headwidth=10,headlength=10)
axes.set_title('(a) SST & shear, El Niño',pad=2,loc="left")
axes.add_patch(mpatches.Rectangle(xy=[360-80, 10], width=60, height=10
            ,edgecolor="g", lw=1, facecolor='none',transform=ccrs.PlateCarree()))
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.5, color='gray', alpha=0.5, linestyle='-')
gl.ylocator = mticker.FixedLocator([-20, 0, 20, 40, 60])
gl.xlocator = mticker.FixedLocator([-150, -90, -30])
#gl.left_labels = True
gl.right_labels = False
gl.top_labels = False



# La Nina:
# --------
axes=fig.add_subplot(2,2,2, projection=ccrs.PlateCarree(0))
axes.set_extent([-170, 10, -20.01, 60.01], crs=ccrs.PlateCarree())
axes.coastlines(resolution='110m',lw=0.3)
axes.stock_img()
plt.set_cmap('bwr')
DATA=1.0*SST_composite_LaNina[:,:]
c=axes.pcolormesh(lon, lat, DATA[:,:], vmin=-3, vmax=3, shading='auto')
clb=plt.colorbar(c, pad=0.02, shrink=0.55, ax=axes)
clb.set_label('°C')
s=4
axes.quiver(lon[::s], lat[::s], U_LN[::s,::s], V_LN[::s,::s],scale=400\
            ,width=0.001,headwidth=10,headlength=10)
axes.set_title('(b) SST & shear, La Niña',pad=2,loc="left")
axes.add_patch(mpatches.Rectangle(xy=[360-80, 10], width=60, height=10
            ,edgecolor="g", lw=1, facecolor='none',transform=ccrs.PlateCarree()))
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.5, color='gray', alpha=0.5, linestyle='-')
gl.xlocator = mticker.FixedLocator([-150, -90, -30])
gl.left_labels = False
gl.right_labels = False
gl.top_labels = False


# El Nino minus La Nina:
# ----------------------
axes=fig.add_subplot(2,2,(3,4), projection=ccrs.PlateCarree(0))
axes.set_extent([-170, 10, -20.01, 60.01], crs=ccrs.PlateCarree())
axes.coastlines(resolution='110m',lw=0.3)
axes.stock_img()
plt.set_cmap('bwr')
DATA=(shear_magnitude_EN-shear_magnitude_LN)*mask
c=axes.pcolormesh(lon, lat, DATA[:,:], vmin=-15, vmax=15, shading='auto')
clb=plt.colorbar(c, pad=0.02, ax=axes)
clb.set_label("m/s")
s=4
U=U_EN[::s,::s]-U_LN[::s,::s]
V=V_EN[::s,::s]-V_LN[::s,::s]
axes.quiver(lon[::s], lat[::s], U, V,scale=400,width=0.001\
            ,headwidth=10,headlength=10)
axes.set_title('(c) Shear, El Niño $-$ La Niña',pad=2,loc="left")
axes.add_patch(mpatches.Rectangle(xy=[360-80, 10], width=60, height=10
        ,edgecolor="g", lw=1, facecolor='none', transform=ccrs.PlateCarree()))
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.5, color='gray', linestyle='-')
gl.ylocator = mticker.FixedLocator([-20, 0, 20, 40, 60])
gl.right_labels = False
gl.top_labels = False

# finalize and show plot:
# plt.subplots_adjust(top=0.92, bottom=0.08, left=0.05, right=0.99\
#                      ,hspace=0.07,wspace=0.01);
#move bottom panel and its colorbar to left a bit:
if 1:
    move = 0.02
    box = axes.get_position()
    box.x0 = box.x0 - move
    box.x1 = box.x1 - move
    axes.set_position(box)
    cbox=clb.ax.get_position()
    cbox.x0 = cbox.x0 - move
    cbox.x1 = cbox.x1 - move
    clb.ax.set_position(cbox)

plt.pause(1)

print("saving to png and pdf...")
filename="hurricanes-SST-and-jet-shear-ENSO-composites-ERA5"
fig.savefig("Output/"+filename+".pdf", pad_inches=0.02, dpi=400)
# png = "Output/"+filename+".png"
# pdf = "Output/"+filename+".pdf"
# subprocess.run(["magick", png, pdf], check=True);

print("done.")
