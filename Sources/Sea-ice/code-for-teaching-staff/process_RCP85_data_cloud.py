# Read sea ice area fraction projections from CESM's SSP585; create a
# pickle file for September sea ice concentration map every five years.
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import scipy as scipy
import xarray as xr
import intake

# open cloud data with intake-esm
# -----------------------------
cat_url = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
col = intake.open_esm_datastore(cat_url)

query = dict(
    source_id=["CESM2-WACCM"],      
    experiment_id=["ssp585"],  
    table_id=["SImon"],          
    variable_id=["siconc"], 
    institution_id=["NCAR"]      
)

cat_SI = col.search(**query)

# Select the first ensemble member (zstore), there's 5 total:
zstore_url = cat_SI.df['zstore'].values[0]
ds = xr.open_zarr(
    zstore_url,
    storage_options={"anon": True},
    consolidated=False
)


# get times of needed september data every 5 years:
# -------------------------------------------------
ds_sept = ds.sel(time=ds['time.month'] == 9)
ds_sept_5yr = ds_sept.isel(time=slice(0, None, 5))
selected_times = ds_sept_5yr.time.values
sic_concentration_rcp85_sept_years = ds_sept_5yr.time.dt.year.values
N_files = len(selected_times)


# loop over files, extract September data every five years only:
# --------------------------------------------------------------

for i, t in enumerate(selected_times):
    sic = ds.siconc.sel(time=t).values
    sic[sic > 1.e10] = np.nan

    if i == 0:
        lon_input = ds.lon.values
        lat_input = ds.lat.values
        lon1=1.0*lon_input[lon_input<1.e10]
        lat1=1.0*lat_input[lat_input<1.e10]

    # interpolate to a regular lat,lon grid:
    # --------------------------------------
    DATA=sic
    lon=np.arange(0.5,360.5,1)
    lat=np.arange(-89.5,90.5,1)
    points=np.vstack((lon1.flatten(),lat1.flatten()))
    sic_concentration_rcp85_sept_lon,sic_concentration_rcp85_sept_lat=np.meshgrid(lon,lat)
    Ny,Nx=sic_concentration_rcp85_sept_lon.shape
    values=DATA[lat_input<1.0e10].flatten()
    seaice_regular_grid=scipy.interpolate.griddata(points.T,values
                             ,(sic_concentration_rcp85_sept_lon
                             ,sic_concentration_rcp85_sept_lat)
                             ,method='linear')

    # array for saving regular grid data for students:
    if i == 0:
        sic_concentration_rcp85_sept = np.zeros((N_files, Ny, Nx))
    sic_concentration_rcp85_sept[i,:,:]=seaice_regular_grid


# save variables to be pickled:
np.save("Output/to-pickle/sic_concentration_rcp85_sept.npy", sic_concentration_rcp85_sept)
np.save("Output/to-pickle/sic_concentration_rcp85_sept_lon.npy", sic_concentration_rcp85_sept_lon)
np.save("Output/to-pickle/sic_concentration_rcp85_sept_lat.npy", sic_concentration_rcp85_sept_lat)
np.save("Output/to-pickle/sic_concentration_rcp85_sept_years.npy", sic_concentration_rcp85_sept_years)

    
# plot:
# -----
fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(15, 9), constrained_layout=True,
                         subplot_kw={'projection': ccrs.NorthPolarStereo(central_longitude=0)})
ax=axes.flat

for i, t in enumerate(sic_concentration_rcp85_sept_years):

    # Contour:
    # --------
    ax[i].set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
    ax[i].coastlines(resolution='110m')
    ax[i].gridlines()
    
    cmap = plt.cm.jet.copy()
    cmap.set_bad(color='white')  # make NaNs white
    
    c=ax[i].pcolormesh(sic_concentration_rcp85_sept_lon, sic_concentration_rcp85_sept_lat
                     ,sic_concentration_rcp85_sept[i,:,:]\
                     ,transform=ccrs.PlateCarree(), cmap='jet')
    ax[i].set_title('Year = '+repr(sic_concentration_rcp85_sept_years[i]))
    cb = plt.colorbar(c, ax=ax[i], shrink=0.85, pad=0.02)

# an overall title above all panels:
fig.suptitle("September sea ice concentration (%)", fontsize=16)
plt.pause(1.0)
