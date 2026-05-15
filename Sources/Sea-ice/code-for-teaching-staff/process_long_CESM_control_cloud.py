# Read sea ice area from a long CESM control run from cloud data via
# Pangeo. To be used for detection analysis; create a pickle file with
# monthly time series for students.
import numpy as np
import matplotlib.pyplot as plt
import scipy as scipy
import cartopy.crs as ccrs
import pandas as pd
import xarray as xr
import fsspec
import time

start_time = time.time()

# -------------------------------
# LOAD CMIP6 DATAFRAMES
# -------------------------------
df = pd.read_csv('https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv')
df_SI = df.query("activity_id=='CMIP'& table_id == 'SImon' & institution_id == 'NCAR' & experiment_id == 'piControl' & source_id =='CESM2'")
print("Sea Ice data contained in the zArr store:")
print(np.unique(df_SI["variable_id"]))


# Sea ice concentration
print("extracting sea-ice concentration...")
df_siconc = df_SI.query("variable_id == 'siconc'")
mapper_siconc = fsspec.get_mapper(df_siconc.zstore.values[0])
ds_siconc = xr.open_dataset(
    df_siconc.zstore.values[0],
    engine="zarr",
    backend_kwargs={"storage_options": {"consolidated": None}}
)
tlat = ds_siconc.lat.values
tlon = ds_siconc.lon.values
lat=tlat[tlat<1.e10]
lon=tlon[tlat<1.e10]

# Northern Hemisphere sea-ice area
print("extracting NH sea-ice area...")
df_siarean = df_SI.query("variable_id == 'siarean'")
mapper_siarean = fsspec.get_mapper(df_siarean.zstore.values[0])
ds_siarean = xr.open_dataset(
    df_siarean.zstore.values[0],
    engine="zarr",
    backend_kwargs={"storage_options": {"consolidated": None}}
)

# Create variables to hold time series
# --------------------------------
N_months = ds_siarean.siarean.time.size
sic_CESM_control = ds_siarean.siarean.values  # use pre-integrated NH area
sic_CESM_control_years = np.arange(0, N_months/12.0, 1.0/12.0)


siconc_clean = ds_siconc.siconc.where(ds_siconc.siconc <= 1.e10)

print("interpolating sea ice to regular lon/lat grid...")
# -------------------------------------------------------
DATA=siconc_clean.isel(time=0)
lon1=np.arange(0.5,360.5,1)
lat1=np.arange(-89.5,90.5,1)
points=np.vstack((lon.flatten(),lat.flatten()))
seaice_regular_grid_lon,seaice_regular_grid_lat=np.meshgrid(lon1,lat1)
Ny,Nx=seaice_regular_grid_lon.shape
seaice_regular_grid=np.zeros((Ny,Nx))
values=DATA.values[tlat<1.0e10]
values=values.flatten()
seaice_regular_grid[:,:]=scipy.interpolate.griddata(points.T,values
                    ,(seaice_regular_grid_lon,seaice_regular_grid_lat)
                    ,method='linear')

# Contour the first month to verify that all is well
# --------------------------------------------------
print("contouring...")
plt.figure(1, figsize=(6,6))
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
c = plt.pcolormesh(seaice_regular_grid_lon,seaice_regular_grid_lat,
                   seaice_regular_grid,
                   transform=ccrs.PlateCarree(),
                   cmap='jet')
plt.title('Sea ice area fraction (%) - first month (cloud)')
plt.colorbar(c, shrink=0.85, pad=0.02)
plt.pause(1.0)


plt.figure(2, figsize=(6,6))
plt.plot(sic_CESM_control_years, sic_CESM_control, '-x'
         , label='Pre-integrated NH area')
plt.title("NH sea ice area ($10^6$ km$^2$)")
plt.xlabel("years")
plt.ylabel("Sea ice area (10^6 km²)")
plt.legend()
plt.grid(True)
plt.pause(1.0)


# save variables to be pickled:
np.save("Output/to-pickle/sic_CESM_control",sic_CESM_control)
np.save("Output/to-pickle/sic_CESM_control_years.npy",sic_CESM_control_years)

end_time = time.time()
print(f"Elapsed time: {end_time - start_time:.2f} seconds")
