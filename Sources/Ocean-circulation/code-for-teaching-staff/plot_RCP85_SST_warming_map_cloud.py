# plot SST warming (GFDL-CM4, CMIP6) from cloud:
# warming = mean(2090–2100, ssp585) - mean(2000–2010, historical)

import numpy as np
import xarray as xr
import intake
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.ticker as mticker
from scipy import interpolate

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

# -------------------------
# Settings
# -------------------------
SOURCE_ID   = "GFDL-CM4"
VARIABLE_ID = "tos"      # SST (degC)
TABLE_ID    = "Omon"
MEMBER_ID   = "r1i1p1f1"
GRID_LABEL  = "gn"

BASELINE = ("2000-01-01", "2010-12-31")
FUTURE   = ("2040-01-01", "2050-12-31")

# -------------------------
# Open CMIP6 cloud catalog
# -------------------------
CATALOG_URL = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
col = intake.open_esm_datastore(CATALOG_URL)

def open_one(experiment_id: str, activity_id: str) -> xr.Dataset:
    sub = col.search(
        source_id=SOURCE_ID,
        activity_id=activity_id,
        experiment_id=experiment_id,
        table_id=TABLE_ID,
        member_id=MEMBER_ID,
        grid_label=GRID_LABEL,
        variable_id=VARIABLE_ID,
    )
    dsets = sub.to_dataset_dict(zarr_kwargs={"consolidated": True})
    return next(iter(dsets.values()))

ds_hist = open_one("historical", "CMIP")
ds_fut  = open_one("ssp585",    "ScenarioMIP")

da_hist = ds_hist[VARIABLE_ID].squeeze(drop=True)  # (time, y, x)
da_fut  = ds_fut[VARIABLE_ID].squeeze(drop=True)

# 2-D curvilinear grid
lat = ds_hist["lat"]
lon = ds_hist["lon"]
lon = (((lon + 180) % 360) - 180)  # put lon in [-180, 180)

# -------------------------
# Compute warming
# -------------------------
hist_base = da_hist.sel(time=slice(*BASELINE)).mean("time", skipna=True)
fut_mean  = da_fut.sel(time=slice(*FUTURE)).mean("time", skipna=True)
DATA   = (fut_mean - hist_base).compute()

lat = lat.compute()
lon = lon.compute()

# interpolate to a regular lon/lat grid using "nearest" method to get
# rid of the gap in longitude:
lon = ((lon + 180) % 360) - 180
x = np.arange(-180, 180.25, 0.25)
y = np.arange(-90, 90.25, 0.25)
mylon, mylat = np.meshgrid(x, y)

x = lon.values.ravel()
y = lat.values.ravel()
d = DATA.values.ravel()
myDATA=interpolate.griddata((x, y), d, (mylon,mylat), method='nearest')
lon=mylon;lat=mylat;DATA=myDATA

# -------------------------
# Plot
# -------------------------
fig=plt.figure(figsize=(4,4),dpi=200)
ax=fig.add_subplot(1,1,1, projection=ccrs.Orthographic(-45, 45))

# add coastlines:
ax.stock_img()
ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=0.3)
ax.add_feature(cfeature.LAND.with_scale("50m"))

# Draw the contours:
delta=0.25; levels=np.arange(-4,4+delta,delta)
cf = ax.contourf(
    lon, lat, DATA,
    levels=levels,
    cmap="bwr",
    extend="both",
    transform=ccrs.PlateCarree()
)

# colobar:
cb = plt.colorbar(cf, ax=ax, shrink=0.5, pad=0.02, ticks=np.arange(-4, 5, 1))
cb.set_label("°C")

gl = ax.gridlines(color="grey", linewidth=0.25)
gl.ylocator = mticker.FixedLocator(range(-80, 100, 20))

plt.tight_layout()
plt.pause(3)
years_string="_"+BASELINE[0][:4]+"-"+FUTURE[0][:4]
fig.savefig("Output/ocean-circulation-MOC-collapse-SST-warming-SSP585"+years_string+".pdf")

# save data for students
np.save("Output/to-pickle/rcp85_SST_warming_hole_map.npy",DATA)
np.save("Output/to-pickle/rcp85_SST_warming_hole_map_lat.npy",lat)
np.save("Output/to-pickle/rcp85_SST_warming_hole_map_long.npy",lon)
