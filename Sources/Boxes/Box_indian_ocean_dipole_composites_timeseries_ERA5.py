# Calculate SST and wind composites and IOD time series for IOD+/-,
# for climate Box Using ERA5.

# load libraries, read time series data:
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from netCDF4 import num2date
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from datetime import datetime, timedelta
import matplotlib.patches as mpatches
import cdsapi
from pathlib import Path
import urllib.request


# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'
fontsize=9
tick_label_fontsize=9
plt.rcParams['font.size'] = fontsize
plt.rcParams.update({'font.size': fontsize})

# read atmospheric grid information:
data_dir = Path.home() / "Downloads"

# ERA5 download:
years  = [str(y) for y in range(1979, 2026)]
months = [f"{m:02d}" for m in range(1, 13)]
time   = ["00:00"]

c = cdsapi.Client()

common = {
    "product_type": "monthly_averaged_reanalysis",
    "year": years,
    "month": months,
    "time": "00:00",
    "format": "netcdf",
    "grid": [1.0, 1.0],
}

print("reading ERA5 data...")
if not (data_dir / "SST.nc").is_file():
    print("downloading SST...")
    c.retrieve(
        "reanalysis-era5-single-levels-monthly-means",
        {**common, "variable": ["sea_surface_temperature"]},
        data_dir / "SST.nc",
    )

if not (data_dir / "U10.nc").is_file():
    print("downloading U10...")
    c.retrieve(
        "reanalysis-era5-single-levels-monthly-means",
        {**common, "variable": ["10m_u_component_of_wind"]},
        data_dir / "U10.nc",
    )

if not (data_dir / "V10.nc").is_file():
    print("downloading V10...")
    c.retrieve(
        "reanalysis-era5-single-levels-monthly-means",
        {**common, "variable": ["10m_v_component_of_wind"]},
        data_dir / "V10.nc",
    )

print("done.")
    
# Also normalize in case files already existed from previous downloads
# for p in [u10_path, v10_path, sst_path]:
#     if os.path.exists(p) and os.path.getsize(p) > 0:
#         _normalize_time_var_to_time(p)
        
file="SST.nc"
ncfile = Dataset(data_dir / file, 'r');
lat = ncfile.variables['latitude'][:]
lon = ncfile.variables['longitude'][:]
times=ncfile.variables['valid_time']

# open SST file:
file="SST.nc"
ncfile= Dataset(data_dir / file, 'r');
SST= ncfile.variables['sst']

# open U,V files:
file="U10.nc"
ncfile= Dataset(data_dir / file, 'r');
U10= ncfile.variables['u10']
file="V10.nc"
ncfile= Dataset(data_dir / file, 'r');
V10 = ncfile.variables['v10']

# get grid/ time limits:
Nt,Ny,Nx=U10.shape

# calculate dates and month for each day in the record:
dates = num2date(times, units=times.units, calendar=times.calendar)
# matplotlib can't plot cftime objects; convert to plain datetime:
dates = [datetime(d.year, d.month, d.day, d.hour, d.minute, int(d.second)) for d in dates]
months = np.array([d.month for d in dates])
print("calculated months time series.")

# initialize monthly climatoloigy arrays:
U10_climatology=np.zeros((12,Ny,Nx))
V10_climatology=np.zeros((12,Ny,Nx))
SST_climatology=np.zeros((12,Ny,Nx))

print("dimensions of U10,V10:",U10.shape)
print("dimensions of SST:",SST.shape)
print("first time:",dates[0],",last time:",dates[-1])


# Read pre-calculated IOD time series from NOAA that is updated regularly:

# %%
# Initialize lists to store monthly values and corresponding times
monthly_values = []
times_IOD = []

# Open the data file
print("reading IOD index from NOAA site...")
url = "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data"
with urllib.request.urlopen(url) as resp:
    # resp yields bytes; decode to text lines
    lines = (line.decode("utf-8", errors="replace") for line in resp)
    # Skip the first line
    next(lines)
    for line in lines:
        # Split the line into tokens
        tokens = line.strip().split()
        if not tokens:
            continue  # Skip empty lines
        # Convert the first token to float to get the year
        year = float(tokens[0])
        # Stop reading if the year is -9999
        if year == -9999:
            break
        # Extract the twelve monthly values
        months_IOD = tokens[1:]
        # Check if there are exactly 12 monthly values
        if len(months_IOD) != 12:
            print(f"Warning: Year {int(year)} does not have 12 monthly values.")
            continue
        # Process each month's value
        for idx, val in enumerate(months_IOD):
            val_float = float(val)
            # Handle -9999 as NaN
            if val_float == -9999:
                monthly_values.append(np.nan)
            else:
                monthly_values.append(val_float)
            # Calculate the time for each month
            time = year + (idx + 0.5) / 12
            times_IOD.append(time)

# Convert lists to NumPy arrays
monthly_IOD_values_array = np.array(monthly_values)
monthly_IOD_times_array = np.array(times_IOD)

print("done.")

# define some functions to be able to process all files efficiently
# without running into memory problems:

def calculate_SST_index_timeseries(lat_min,lat_max,lon_min,lon_max):
    """ calculate a monthly time series of IOD."""
    print("calculate_SST_index_timeseries... ",end="")
    index_timeseries=np.zeros(len(times))
    # produce index arrays in lat and lon used for averaging over desired region:
    ilat=np.logical_and(lat<=lat_max,lat>=lat_min)
    ilon=np.logical_and(lon<=lon_max,lon>=lon_min)
    # calculate spatial average to find time index:
    index_timeseries=np.nanmean(SST[:,ilat,ilon],axis=(1,2))

    # now remove monthly climatology from the NINO3 time series:
    index_monthly_climatology=np.zeros(12)
    for m in range(12):
        index_monthly_climatology[m]=np.mean(index_timeseries[m::12])
        index_timeseries[m::12]= \
           index_timeseries[m::12]-index_monthly_climatology[m]

    print(" done.")
    return index_timeseries


def calculate_composite(variable,mask_timeseries,remove_monthly_climatology,monthly_climatology):
    first_time_read=True
    iavg=0
    for t in range(len(times)):
        #print(t,",",end="")
        # read data:
        if not np.isnan(mask_timeseries[t]):
            #print(t,",",end="")
            if first_time_read:
                first_time_read=False
                variable_avg=1.0*variable[t,:,:]
            else:
                variable_avg=variable_avg+variable[t,:,:]
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

# calculate IOD index:

# east indian ocean:
lat_min=-10
lat_max=0
lon_min=90
lon_max=110
IOD_east_timeseries=calculate_SST_index_timeseries(lat_min,lat_max,lon_min,lon_max)
IOD_east_timeseries=IOD_east_timeseries[0:len(dates)]
#plt.plot(IOD_east,lw=1)

# west indian ocean:
lat_min=-10
lat_max=10
lon_min=50
lon_max=70
IOD_west_timeseries=calculate_SST_index_timeseries(lat_min,lat_max,lon_min,lon_max)
IOD_west_timeseries=IOD_west_timeseries[0:len(dates)]

IOD_timeseries=IOD_west_timeseries-IOD_east_timeseries

# prepare mask time series for calculating composites:

mean=np.mean(IOD_timeseries)
std=np.std(IOD_timeseries)
print("IOD mean, std=",mean,std)
IODp_threshold=mean+std*1
IODm_threshold=mean-std*1

# calculate masks:
IODp_mask_timeseries=IOD_timeseries*0+1.0
IODp_mask_timeseries[IOD_timeseries<IODp_threshold]=np.nan
num_IODp_months=np.nansum(IODp_mask_timeseries)


IODm_mask_timeseries=IOD_timeseries*0+1.0
IODm_mask_timeseries[IOD_timeseries>IODm_threshold]=np.nan
num_IODm_months=np.nansum(IODm_mask_timeseries)


print("IODp_threshold=",IODp_threshold, ", number of IODp months=",num_IODp_months
      ,"=",100*num_IODp_months/len(IOD_timeseries),"%");
print("IODm_threshold=",IODm_threshold, ", number of IODp months=",num_IODm_months
      ,"=",100*num_IODm_months/len(IOD_timeseries),"%");

print("done.")

# use indices to calculate monthly climatologies and composites:
print("Calculating monthly climatologies...",end="")
remove_monthly_climatology=False
for m in range(0,12):
    print(m,",",end="")
    climatology_mask_timeseries=np.zeros(IODp_mask_timeseries.shape)*np.nan
    climatology_mask_timeseries[m::12]=1
    monthly_climatology=np.nan
    SST_climatology[m,:,:]=calculate_composite(SST,climatology_mask_timeseries,remove_monthly_climatology,monthly_climatology)
print(" Done calculating monthly climatologies.")

# calculate composites for El Nina and La Nina:
print("Calculating IOD+/- SST composites...",end="")
remove_monthly_climatology=True
SST_composite_IODp=calculate_composite(SST,IODp_mask_timeseries,remove_monthly_climatology,SST_climatology)
SST_composite_IODm=calculate_composite(SST,IODm_mask_timeseries,remove_monthly_climatology,SST_climatology)
print(" Done calculating IOD+/- composites.")
    
print("done.")

# draw the climatologies and composites:
print("location of xticklabels is different in final pdf.")
# initialize figure:
projection=ccrs.PlateCarree(central_longitude=0.0);
fig=plt.figure(figsize=(5,2.5));
shrink=0.62


# IOD+:
# -----
axes=fig.add_subplot(2,6,(1,3), projection=ccrs.PlateCarree(0))
axes.set_extent([10, 160, -40, 30], crs=ccrs.PlateCarree(0))
axes.coastlines(resolution='110m',lw=0.3)
axes.stock_img()
plt.set_cmap('bwr')
DATA=1.0*SST_composite_IODp[:,:]
c=axes.pcolormesh(lon,lat,DATA,vmin=-1,vmax=1)
axes.set_title('(a) IOD$+$',loc="left",pad=3,fontsize=fontsize)
axes.add_patch(mpatches.Rectangle(xy=[50, -10], width=20, height=20,edgecolor="g", lw=1, facecolor='none',transform=ccrs.PlateCarree()))
axes.add_patch(mpatches.Rectangle(xy=[90, -10], width=20, height=10,edgecolor="g", lw=1, facecolor='none',transform=ccrs.PlateCarree()))
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                  linewidth=0.25, color='gray', alpha=0.5, linestyle='-')
gl.left_labels = True
gl.bottom_labels = True
# add tick makrs, labels are already dealt with by cartopy, so turn that off.
# axes.set_xticks([20, 50, 80, 110, 140])
# axes.set_xticklabels("")
gl.xlocator = mticker.FixedLocator([20, 50, 80, 110, 140])
gl.rotate_labels=False
#gl.xpadding=20 # space between xtick labes and plot
#gl.right_labels = False
#gl.top_labels = False
gl.ypadding=2
gl.xpadding=3


# IOD-:
# -----
axes=fig.add_subplot(2,6,(4,6), projection=ccrs.PlateCarree(0))#grid[0, 0])
axes.set_extent([10, 160, -40, 30], crs=ccrs.PlateCarree())
axes.coastlines(resolution='110m',lw=0.3)
axes.stock_img()
plt.set_cmap('bwr')
DATA=1.0*SST_composite_IODm[:,:]
c=axes.pcolormesh(lon,lat,DATA,vmin=-1,vmax=1)
axes.set_title('(b) IOD$-$',loc="left",pad=3,fontsize=fontsize)
#axes.text(0.03, 0.93, "(b)", transform=axes.transAxes, fontsize=12,
#        verticalalignment='top', bbox=props)
axes.add_patch(mpatches.Rectangle(xy=[50, -10], width=20, height=20,edgecolor="g" \
                , lw=1, facecolor='none',transform=ccrs.PlateCarree()))
axes.add_patch(mpatches.Rectangle(xy=[90, -10], width=20, height=10,edgecolor="g" \
                , lw=1, facecolor='none',transform=ccrs.PlateCarree()))
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                  linewidth=0.25, color='gray', alpha=0.5, linestyle='-')
gl.bottom_labels = True
# add tick makrs, labels are already dealt with by cartopy, so turn that off.
# axes.set_xticks([20, 50, 80, 110, 140])
# axes.set_xticklabels("")
gl.xlocator = mticker.FixedLocator([20, 50, 80, 110, 140])
gl.rotate_labels=False
#gl.xpadding=20 # space between xtick labes and plot
#gl.left_labels = False
#gl.right_labels = False
#gl.top_labels = False
gl.ypadding=2
gl.xpadding=3

# joint colorbar for both upper panels:
ax2 = fig.add_axes([0.86, 0.63, 0.01, 0.30])
clb=fig.colorbar(c,cax=ax2, ticks=np.arange(-1,1.5,0.5),anchor=(0.3,0.5))
clb.set_label('°C',labelpad=0)



# IOD time series:
# ------------------
std=np.std(IOD_timeseries)
axes=fig.add_subplot(2,6,(9,11))
axes.plot(monthly_IOD_times_array, monthly_IOD_values_array,lw=0.5,label="IOD",color="k")
plt.yticks([-1,0,1,2])
y1=1.0*monthly_IOD_values_array
y1[monthly_IOD_values_array<std]=np.nan
y1=y1*0+std
axes.fill_between(monthly_IOD_times_array, y1=y1, y2=monthly_IOD_values_array, color="r")
y2=1.0*monthly_IOD_values_array
y2[monthly_IOD_values_array>-std]=np.nan
y2=y2*0-std
axes.fill_between(monthly_IOD_times_array, y1=monthly_IOD_values_array, y2=y2, color="b")
axes.set_xlabel("Year")
axes.set_ylabel("IOD (°C)")
axes.set_title("(c)",loc="left",pad=3,fontsize=fontsize)
plt.xlim(1978, 2025);
plt.ylim(-1.2,1.4)
axes.grid(lw=0.25);

axes.set_facecolor('#f2f2f2')
fig.patch.set_facecolor('#f2f2f2')

# finalize and show plot:
plt.subplots_adjust(left=0.03,right=0.97,bottom=0.17,top=0.93,hspace=0.45,wspace=-0.65);
plt.show()

fig.savefig("Output/Box-IOD-composites-timeseries-ERA5.pdf",facecolor='#f2f2f2'
            ,bbox_inches='tight',pad_inches=0, dpi=600);

print("done.")
