# ## Calculate SST and wind composites and NINO3 time series for El Nino and La Nina, for climate Box. Using ERA5.

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


# define some functions to be able to process all files efficiently without running into memory problems

def calculate_SST_index_timeseries():
    """ calculate a monthly time series of NINO3.4."""
    print("calculate_SST_index_timeseries... ",end="")
    index_timeseries=np.zeros(len(times))
    ilat=np.logical_and(lat<=5,lat>=-5)
    ilon=np.logical_and(lon<=360-120,lon>=360-170)
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

# Read pre-calculated NINO3.4 time series from
# https://psl.noaa.gov/data/correlation/nina34.anom.data

# Initialize lists to store monthly values and corresponding times
monthly_values = []
times_nino34 = []

# Open the remote data file
url = "https://psl.noaa.gov/data/correlation/nina34.anom.data"

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
        # Stop reading if the year is -99.99
        if year == -99.99:
            break
        # Extract the twelve monthly values
        months_nino34 = tokens[1:]
        # Check if there are exactly 12 monthly values
        if len(months_nino34) != 12:
            print(f"Warning: Year {int(year)} does not have 12 monthly values.")
            continue
        # Process each month's value
        for idx, val in enumerate(months_nino34):
            val_float = float(val)
            # Handle -99.99 as NaN
            if val_float == -99.99:
                monthly_values.append(np.nan)
            else:
                monthly_values.append(val_float)
            # Calculate the time for each month
            time = year + (idx + 0.5) / 12
            times_nino34.append(time)

# Convert lists to NumPy arrays
monthly_nino34_values_array = np.array(monthly_values)
monthly_nino34_times_array = np.array(times_nino34)

print("done.")

# Calculate Nino3.4 from reanalysis data:
NINO34_timeseries=calculate_SST_index_timeseries()
NINO34_timeseries=NINO34_timeseries[0:len(dates)]

# prepare mask time series for calculating composites:
mean=np.mean(NINO34_timeseries)
std=np.std(NINO34_timeseries)
print("nino3.4 mean, std=",mean,std)
ElNino_threshold=mean+std*1
LaNina_threshold=mean-std*1

# calculate masks:
ElNino_mask_timeseries=NINO34_timeseries*0+1.0
ElNino_mask_timeseries[NINO34_timeseries<ElNino_threshold]=np.nan
num_ElNino_months=np.nansum(ElNino_mask_timeseries)

LaNina_mask_timeseries=NINO34_timeseries*0+1.0
LaNina_mask_timeseries[NINO34_timeseries>LaNina_threshold]=np.nan
num_LaNina_months=np.nansum(LaNina_mask_timeseries)


print("ElNino_threshold = %4.4g, number of ElNino months = %d = %3.3g percent" \
      % (ElNino_threshold, num_ElNino_months,100*num_ElNino_months/len(NINO34_timeseries)) \
      )
print("LaNina_threshold = %4.4g, number of LaNina months = %d = %3.3g percent" \
      % (LaNina_threshold, num_LaNina_months, 100*num_LaNina_months/len(NINO34_timeseries)) \
      )

print("done.")

# use indices to calculate monthly climatologies and composites:
print("Calculating monthly climatologies...",end="")
remove_monthly_climatology=False
for m in range(0,12):
    print(m,",",end="")
    climatology_mask_timeseries=np.zeros(ElNino_mask_timeseries.shape)*np.nan
    climatology_mask_timeseries[m::12]=1
    monthly_climatology=np.nan
    U10_climatology[m,:,:] = calculate_composite(U10,climatology_mask_timeseries,remove_monthly_climatology,monthly_climatology)
    V10_climatology[m,:,:] = calculate_composite(V10,climatology_mask_timeseries,remove_monthly_climatology,monthly_climatology)
    SST_climatology[m,:,:] = calculate_composite(SST,climatology_mask_timeseries,remove_monthly_climatology,monthly_climatology)
print(" Done calculating monthly climatologies.")

# calculate composites for El Nina and La Nina:
print("Calculating El Nino/ La Nina composites...",end="")
remove_monthly_climatology=True
SST_composite_ElNino = calculate_composite(SST,ElNino_mask_timeseries,remove_monthly_climatology,SST_climatology)
SST_composite_LaNina = calculate_composite(SST,LaNina_mask_timeseries,remove_monthly_climatology,SST_climatology)
U10_composite_ElNino = calculate_composite(U10,ElNino_mask_timeseries,remove_monthly_climatology,U10_climatology)
V10_composite_ElNino = calculate_composite(V10,ElNino_mask_timeseries,remove_monthly_climatology,V10_climatology)
U10_composite_LaNina = calculate_composite(U10,LaNina_mask_timeseries,remove_monthly_climatology,U10_climatology)
V10_composite_LaNina = calculate_composite(V10,LaNina_mask_timeseries,remove_monthly_climatology,V10_climatology)
print(" Done calculating El Nino/ La Nina composites.")
    
print("done.")

# draw the climatologies and composites:
# add a column to lon/lat arrays to eliminate white gap at dateline:
# for atmospheric plots:
lon1=1.0*lon[-1]+lon[2]-lon[1]; lon1=np.hstack((lon,lon1))

# initialize figure:
projection=ccrs.PlateCarree(central_longitude=0.0);
fig=plt.figure(figsize=(5,2.5));


# El Nino:
# --------
axes=fig.add_subplot(2,6,(1,3), projection=ccrs.PlateCarree(180))
axes.set_extent([-220.0, -70.0, -30.01, 30.01], crs=ccrs.PlateCarree(0))
axes.coastlines(resolution='110m',lw=0.3)
axes.stock_img()
plt.set_cmap('bwr')
DATA=1.0*SST_composite_ElNino[:,:]
# add a column to DATA array to eliminate white gap at dateline:
DATA1=1.0*DATA[:,0]; 
DATA1.shape=(len(DATA1[:]),1); DATA1=np.hstack((DATA,DATA1))
c=axes.pcolormesh(lon1+180,lat, DATA1[:,:],vmin=-3,vmax=3)
s=3
axes.quiver(lon[::s]+180, lat[::s], U10_composite_ElNino[::s,::s] \
            , V10_composite_ElNino[::s,::s]\
            ,scale=80,width=0.001,headwidth=10,headlength=12)
axes.set_title('(a) El Niño',loc="left", pad=-1, fontsize=fontsize)
axes.add_patch(mpatches.Rectangle(xy=[360-170, -5], width=50, height=10
                ,edgecolor="g", lw=1, facecolor='none',transform=ccrs.PlateCarree()))
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,  
                  linewidth=0.5, color='gray', alpha=0.5, linestyle='-')
gl.xlocator = mticker.FixedLocator([150, 180, -150, -120, -90])
gl.ylocator = mticker.FixedLocator([-30, -10, 10, 30])
gl.rotate_labels=False
gl.xlabel_style = {'size': tick_label_fontsize}
gl.ylabel_style = {'size': tick_label_fontsize}
gl.right_labels = False
gl.top_labels = False
gl.ypadding=2
gl.xpadding=3


# La Nina:
# --------
axes=fig.add_subplot(2,6,(4,6), projection=ccrs.PlateCarree(180))
axes.set_extent([-220.0, -70.0, -30.01, 30.01], crs=ccrs.PlateCarree())
axes.coastlines(resolution='110m',lw=0.3)
axes.stock_img()
plt.set_cmap('bwr')
DATA=1.0*SST_composite_LaNina[:,:]
# add a column to DATA array to eliminate white gap at dateline:
DATA1=1.0*DATA[:,0]; 
DATA1.shape=(len(DATA1[:]),1); DATA1=np.hstack((DATA,DATA1))
c=axes.pcolormesh(lon1+180,lat, DATA1[:,:],vmin=-3,vmax=3)
s=3
axes.quiver(lon[::s]+180, lat[::s], U10_composite_LaNina[::s,::s] \
            , V10_composite_LaNina[::s,::s]\
            ,scale=80,width=0.001,headwidth=10,headlength=12)
axes.set_title('(b) La Niña',loc="left",pad=3,fontsize=fontsize)
axes.add_patch(mpatches.Rectangle(xy=[360-170, -5], width=50, height=10
                ,edgecolor="g", lw=1, facecolor='none',transform=ccrs.PlateCarree()))
gl = axes.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.5, color='gray', alpha=0.5, linestyle='-')
gl.xlocator = mticker.FixedLocator([150, 180, -150, -120, -90])
gl.ylocator = mticker.FixedLocator([-30, -10, 10, 30])
gl.rotate_labels=False
gl.xlabel_style = {'size': tick_label_fontsize}
gl.left_labels = False
gl.right_labels = False
gl.top_labels = False
gl.xpadding=3

# joint colorbar for both upper panels:
ax2 = fig.add_axes([0.91, 0.64, 0.01, 0.29])
clb=fig.colorbar(c,cax=ax2, ticks=np.arange(-3,4,1),anchor=(0.3,0.5))
clb.set_label('°C',labelpad=0)



# NINO3 time series:
# ------------------
# at this point used pre-calculatee NOAA nino3.4 
# instead of the one I calculated from reanalysis:
NINO34_timeseries=np.array(monthly_nino34_values_array)
dates=np.array(monthly_nino34_times_array)
std=np.nanstd(NINO34_timeseries)
axes=fig.add_subplot(2,6,(8,11))
axes.plot(dates,NINO34_timeseries,lw=0.5,label="NINO3.4",color="k")
y1=1.0*NINO34_timeseries
y1[NINO34_timeseries<std]=np.nan
y1=y1*0+std
axes.fill_between(dates, y1=y1, y2=NINO34_timeseries, color="r")
y2=1.0*NINO34_timeseries
y2[NINO34_timeseries>-std]=np.nan
y2=y2*0-std
axes.fill_between(dates, y1=NINO34_timeseries, y2=y2, color="b")
axes.set_xlabel("Year")
axes.set_ylabel("Nino 3.4 (°C)")
plt.xlim([1979,dates[-1]]);
axes.grid(lw=0.25);
axes.set_title("(c)", pad=3, loc="left")
axes.set_facecolor('#f2f2f2')
fig.patch.set_facecolor('#f2f2f2')

# finalize and show plot:
# plt.tight_layout(pad=1, h_pad=0.2, w_pad=-6.8)
plt.subplots_adjust(bottom=0.15,top=0.95,hspace=0.4)

plt.pause(2)
# fig.savefig("Output/Box-ElNino-composites-timeseries-ERA5.pdf",facecolor='#f2f2f2'
#            ,bbox_inches='tight',pad_inches = 0);
filename="Box-ElNino-composites-timeseries-ERA5"
fig.savefig("Output/"+filename+".pdf"
            ,bbox_inches="tight", pad_inches=0.02, dpi=1200)

print("done.")
