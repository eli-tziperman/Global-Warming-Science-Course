import intake
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

# =====================================================
# CONFIG
# =====================================================
OUT_DIR = "./Output"

# Main Development Region (MDR) and hurricane season
LAT_MIN, LAT_MAX = 10, 25
LON_MIN, LON_MAX = 280, 340   # 80W–20W
SEASON_MONTHS = [6, 7, 8, 9, 10, 11]  # JJASON

# CMIP6 specification
SOURCE_ID = "CESM2"
MEMBER_ID = "r11i1p1f1"
TABLE_ID = "Omon"
VARIABLE = "tos"
GRID_LABEL = "gn"

CATALOG_URL = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
#CATALOG_URL = "https://cmip6-pds.s3.amazonaws.com/pangeo-cmip6.json"

# =====================================================
# DATA ACCESS
# =====================================================

def get_observed_sst():
   # NOAA PSL OPeNDAP endpoint for monthly ERSSTv5
   url = "https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc"

   # Open lazily with dask (no full download)
   ds = xr.open_dataset(
       url,
       engine="netcdf4",        # explicit OPeNDAP engine
       chunks={"time": 12},     # 1-year chunks in time (tune as you like)
       decode_times=True,
   )

   # SST (degC), on a 2°x2° lat–lon grid, monthly from 1854-present
   sst = ds["sst"]

   # Convert back to a Dataset:
   ds_out = sst.to_dataset(name="sst")
   return ds_out


def open_cmip6_ds(col, experiment_id):
    subset = col.search(
        source_id=SOURCE_ID,
        experiment_id=experiment_id,
        variable_id=VARIABLE,
        table_id=TABLE_ID,
        member_id=MEMBER_ID,
        grid_label=GRID_LABEL
    )
    dsdict = subset.to_dataset_dict(zarr_kwargs={"consolidated": True})
    if not dsdict:
        raise RuntimeError(f"No dataset found for {experiment_id}")
    key = list(dsdict.keys())[0]
    return dsdict[key]


# =====================================================
# PREPROCESSING
# =====================================================
def preprocess_obs_sst_ds(obj):
    """
    Preprocess observed ERSST SST so it looks like the CESM2 tos field
    from preprocess_tos_ds, i.e.:

    - DataArray with dims (time, nlat, nlon)
    - Coordinates 'lat' and 'lon' as 2D fields with dims (nlat, nlon)
    - lon in 0–360
    - SST in °C
    """

    # input data:
    da = obj["sst"]

    # Normalize longitude to 0–360 if present
    da = da.assign_coords(lon=(da.lon % 360))

    # Rename spatial dimensions from (lat, lon) → (nlat, nlon)
    dim_rename = {}
    dim_rename["lat"] = "nlat"
    dim_rename["lon"] = "nlon"
    da = da.rename(dim_rename)

    # Build 2D lat/lon coordinates on the (nlat, nlon) grid
    # lat1d: (nlat,), lon1d: (nlon,)
    lat1d = da["nlat"]
    lon1d = da["nlon"]

    # Broadcast to 2D arrays with dims (nlat, nlon)
    lat2d, lon2d = xr.broadcast(lat1d, lon1d)

    # Attach as coordinates named 'lat' and 'lon' (like in CESM2)
    da = da.assign_coords(lat=lat2d, lon=lon2d)

    # Kelvin → Celsius check (ERSST should already be °C, so this should NOT trigger)
    sample = float(da.isel(time=0).mean().compute())
    if sample > 100:
        da = da - 273.15

    return da.squeeze(drop=True), da.lat, da.lon


def preprocess_RCP85_tos_ds(ds):
    """
    Standardize CESM2 tos to:
    - DataArray with dims (time, nlat, nlon)
    - Celsius
    - lon in 0–360
    """
    da = ds[VARIABLE]

    # Select first member if needed
    for dim in ["member_id", "dcpp_init_year"]:
        if dim in da.dims:
            da = da.isel({dim: 0})

    # Normalize longitude
    ds = ds.assign_coords(lon=(ds.lon + 360) % 360)

    # Kelvin → Celsius if needed
    sample = float(da.isel(time=0).mean().compute())
    if sample > 100:
        da = da - 273.15

    # Ensure datetime
    if not np.issubdtype(ds.time.dtype, np.datetime64):
        ds["time"] = xr.decode_cf(ds).time

    return da.squeeze(drop=True), ds["lat"], ds["lon"]


# =====================================================
# MDR JJASON SST CALCULATION (IDENTICAL TO LOCAL)
# =====================================================
def compute_mdr_sst_yearly(da):
    """
    Compute JJASON-mean MDR SST for curvilinear CESM2 grid.
    Scientifically identical to local code.
    """
    # Mask MDR using 2D lat/lon (curvilinear-safe)
    lat2d = da.lat
    lon2d = da.lon

    da_mdr = da.where(
        (lat2d >= LAT_MIN) & (lat2d <= LAT_MAX) &
        (lon2d >= LON_MIN) & (lon2d <= LON_MAX)
    )

    da_season = da_mdr.where(
        da_mdr.time.dt.month.isin(SEASON_MONTHS),
        drop=True
    )

    weights = np.cos(np.deg2rad(lat2d))
    sst_weighted = da_season.weighted(weights).mean(dim=("nlat", "nlon"))
    yearly = sst_weighted.groupby("time.year").mean()

    return yearly.year.values, yearly.values


# =====================================================
# MAIN:
# =====================================================

# OBS:
print("opening observations for SST...")
ds_obs=get_observed_sst()
print("preprocessing observations for SST...")
da_obs, lat, lon = preprocess_obs_sst_ds(ds_obs)
last_year = int(da_obs["time"].dt.year.max())
da_obs = da_obs.sel(time=slice(None, f"{last_year}-12-31"))
print("calculating MDR SST for obs...")
years_obs, SST_obs = compute_mdr_sst_yearly(da_obs)
np.save("Output/SST_MDR_OBS_hurricane_season_years.npy", years_obs)
np.save("Output/SST_MDR_OBS_hurricane_season.npy", SST_obs)

# SSP585:
print("Opening CMIP6 Pangeo catalog...")
col = intake.open_esm_datastore(CATALOG_URL)
ds_ssp = open_cmip6_ds(col, "ssp585")
da_ssp, lat, lon = preprocess_RCP85_tos_ds(ds_ssp)
da_ssp_future = da_ssp.sel(time=slice("2015-01-01", None))
years_rcp, SST_rcp = compute_mdr_sst_yearly(da_ssp_future)
np.save("Output/SST_MDR_RCP85_hurricane_season_years.npy", years_rcp)
np.save("Output/SST_MDR_RCP85_hurricane_season.npy", SST_rcp)

print("Done. Files for students written to:", OUT_DIR)

# =====================================================
# PLOT:
# =====================================================
plt.figure(figsize=(4, 4), dpi=300)
plt.plot(years_obs, SST_obs, color="b",lw=1)
plt.plot(years_rcp, SST_rcp, color="r",lw=1)
plt.xlabel("Year")
plt.ylabel("SST (°C)")
plt.title("obs and RCP8.5 MDR SST")
plt.xlim(1850,2100)
plt.ylim(26,31)
plt.grid(lw=0.25)
plt.tight_layout()
plt.show()
