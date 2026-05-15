import os
import weakref
import intake
import numpy as np
import xarray as xr
from scipy.interpolate import griddata

# ------------------------------
# Work around a Python 3.13 bug:
# ------------------------------
_orig_finalize = weakref.finalize

class _NoOpFinalizer:
    __slots__ = ("alive",)
    def __init__(self):
        self.alive = False
    def __call__(self, *args, **kwargs):
        return None
    def detach(self):
        return None
def _patched_finalize(obj, func, *args, **kwargs):
    if getattr(func, "__module__", "") == "gcsfs.core" \
       and getattr(func, "__name__", "") == "close_session":
        return _NoOpFinalizer()
    return _orig_finalize(obj, func, *args, **kwargs)
weakref.finalize = _patched_finalize
# end of hack for bug.

# CMIP6 settings:
# ---------------
CATALOG_URL = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
SOURCE_ID = "HadGEM3-GC31-MM"
MEM_NATIVE = "r1i1p1f3"
GRID_NATIVE = "gn"
MEM_ZOSTOGA = "r1i1p1f3"
GRID_ZOSTOGA = "gm"

# Scenarios:
EXP_HIST = "historical"
EXP_FUT = "ssp585"


def _open_one(cat, variable_id, experiment_id, table_id, member_id, grid_label):
    """Open a single dataset and drop any singleton packaging dims."""
    sub = cat.search(
        source_id=SOURCE_ID,
        experiment_id=experiment_id,
        table_id=table_id,
        variable_id=variable_id,
        member_id=member_id,
        grid_label=grid_label,
    )
    ds = next(
        iter(
            sub.to_dataset_dict(
                zarr_kwargs={
                    "consolidated": True,
                    "storage_options": {"token": "anon", "asynchronous": False},
                },
                xarray_open_kwargs={"chunks": {}},  # preserve native zarr chunking
            ).values()
        )
    )

    return ds.squeeze(drop=True)


def _decimal_year_from_time(time):
    """Convert a CFTimeIndex/DatetimeIndex coordinate to decimal years."""
    years = time.dt.year.values.astype(float)
    months = time.dt.month.values.astype(float)
    return years + (months - 0.5) / 12.0


def _interp_to_regular_grid(lon2d, lat2d, field2d, lon_out, lat_out, method="linear"):
    """Interpolate a native curvilinear (lon2d/lat2d) field to a regular grid.

    Keeps land masking by falling back to nearest-neighbor if there are not
    enough near neighbors for linear interpolation.
    """
    x = np.mod(lon2d, 360.0).ravel()
    y = lat2d.ravel()
    v = field2d.ravel().astype(float)

    ok = np.isfinite(x) & np.isfinite(y) & np.isfinite(v)
    if not np.any(ok):
        return np.full((lat_out.size, lon_out.size), np.nan, dtype=float)

    points = np.column_stack([x[ok], y[ok]])
    lon_grid, lat_grid = np.meshgrid(lon_out, lat_out)

    # Linear interpolation requires enough points for a triangulation.
    if method == "linear" and points.shape[0] < 3:
        method = "nearest"

    try:
        return griddata(points, v[ok], (lon_grid, lat_grid), method=method)
    except Exception:
        return griddata(points, v[ok], (lon_grid, lat_grid), method="nearest")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
CAT = intake.open_esm_datastore(CATALOG_URL)

# Regular output grids (teaching-friendly)
sealevel_regular_grid_lon = np.arange(0.0, 360.0, 1.0)
sealevel_regular_grid_lat = np.arange(-80.0, 80.1, 1.0)
sealevel_lon = sealevel_regular_grid_lon
sealevel_lat = sealevel_regular_grid_lat

Temperature_ocean_lon = np.arange(0.0, 360.0, 1.0)
Temperature_ocean_lat = np.arange(-80.0, 80.1, 1.0)

# output folders
os.makedirs("Output/to-pickle", exist_ok=True)

# Load native coordinate grids:
_ds_tmp = _open_one(CAT, "zos", EXP_HIST, "Omon", MEM_NATIVE, GRID_NATIVE)
lon2d = np.asarray(_ds_tmp["longitude"].values)
lat2d = np.asarray(_ds_tmp["latitude"].values)

# Static ocean mask from the first historical timestep
_native_ocean_mask = np.isfinite(_ds_tmp["zos"].isel(time=0).values)

# Interpolate native ocean mask to the regular grids
_ocean_mask_reg_sea = (
    _interp_to_regular_grid(
        lon2d,
        lat2d,
        _native_ocean_mask.astype(np.uint8),
        sealevel_regular_grid_lon,
        sealevel_regular_grid_lat,
        method="nearest",
    )
    > 0.5
)
_ocean_mask_reg_T = (
    _interp_to_regular_grid(
        lon2d,
        lat2d,
        _native_ocean_mask.astype(np.uint8),
        Temperature_ocean_lon,
        Temperature_ocean_lat,
        method="nearest",
    )
    > 0.5
)

# --- Sea level fields (zos) interpolated to the regular 1° grid
for exp in (EXP_HIST, EXP_FUT):
    print(f"scenario = {exp}")

    ds_zos = _open_one(CAT, "zos", exp, "Omon", MEM_NATIVE, GRID_NATIVE)
    zos = ds_zos["zos"]  # (time, j, i)

    years = _decimal_year_from_time(ds_zos["time"])

    # Interpolate only first and last time for the teaching dataset
    print("interpolating sea level to regular lon/lat grid (first & last time)...")
    sl_first = zos.isel(time=0).values
    sl_last = zos.isel(time=-1).values

    print("time = %5.1f" % years[0])
    sealevel_first = _interp_to_regular_grid(
        lon2d, lat2d, sl_first, sealevel_regular_grid_lon, sealevel_regular_grid_lat
    )
    sealevel_first = np.where(_ocean_mask_reg_sea, sealevel_first, np.nan)

    print("time = %5.1f" % years[-1])
    sealevel_last = _interp_to_regular_grid(
        lon2d, lat2d, sl_last, sealevel_regular_grid_lon, sealevel_regular_grid_lat
    )
    sealevel_last = np.where(_ocean_mask_reg_sea, sealevel_last, np.nan)

    sealevel = np.stack([sealevel_first, sealevel_last], axis=0)
    years_out = np.array([years[0], years[-1]])

    if exp == EXP_HIST:
        sealevel_historical = sealevel
        sealevel_historical_years = years_out
    else:
        sealevel_rcp85 = sealevel
        sealevel_rcp85_years = years_out

    print("    done.")

# --- Temperature fields (thetao) interpolated to the regular 1° grid at all levels
for exp in (EXP_HIST, EXP_FUT):
    print(f"scenario = {exp}")

    ds_thetao = _open_one(CAT, "thetao", exp, "Omon", MEM_NATIVE, GRID_NATIVE)
    thetao = ds_thetao["thetao"]  # (time, lev, j, i)

    # Convert lev to meters if needed
    lev = ds_thetao["lev"].values.astype(float)

    # Teaching script uses every-second level (0,2,4,...)
    lev_sel = np.arange(0, len(lev), 2)
    Temperature_ocean_lev = lev[lev_sel]

    print("interpolating Temperature to regular lon/lat grid for all levels...")

    # Use first & last time (analogous to zos); interpolate each selected level
    T_first = thetao.isel(time=0, lev=lev_sel).values
    T_last = thetao.isel(time=-1, lev=lev_sel).values

    nlev = len(lev_sel)
    out_first = np.empty((nlev, len(Temperature_ocean_lat), len(Temperature_ocean_lon)), dtype=float)
    out_last = np.empty_like(out_first)

    for ii in range(nlev):
        depth = Temperature_ocean_lev[ii]
        print(f"depth = {depth:7.1f}")

        slab0 = T_first[ii, :, :]
        slab1 = T_last[ii, :, :]

        # If a slice is fully-masked (no points), _interp_to_regular_grid returns all-NaN
        out0 = _interp_to_regular_grid(lon2d, lat2d, slab0,
                                       Temperature_ocean_lon, Temperature_ocean_lat)
        out1 = _interp_to_regular_grid(lon2d, lat2d, slab1,
                                       Temperature_ocean_lon, Temperature_ocean_lat)

        # Mask land on the regular grid
        out_first[ii, :, :] = np.where(_ocean_mask_reg_T, out0, np.nan)
        out_last[ii, :, :] = np.where(_ocean_mask_reg_T, out1, np.nan)

    if exp == EXP_HIST:
        Temperature_ocean_1850 = out_first
    else:
        Temperature_ocean_2100 = out_last

    print("    done.")

# --- Global-mean sea level time series from zostoga (already global mean)
for exp in (EXP_HIST, EXP_FUT):
    ds = _open_one(CAT, "zostoga", exp, "Omon", MEM_ZOSTOGA, GRID_ZOSTOGA)
    z = ds["zostoga"].astype(float)
    t = _decimal_year_from_time(ds["time"])

    if exp == EXP_HIST:
        GMSL_thermosteric_historical = z.values
        GMSL_thermosteric_historical_years = t
    else:
        GMSL_thermosteric_rcp85 = z.values
        GMSL_thermosteric_rcp85_years = t

# adjust GMSL_thermosteric time series to remove the mean of 1960-1990:
GMSL_mean1960_1990=np.mean(GMSL_thermosteric_historical[
    np.logical_and(
    GMSL_thermosteric_historical_years>=1960,
    GMSL_thermosteric_historical_years<=1990
    )])
GMSL_thermosteric_historical=GMSL_thermosteric_historical-GMSL_mean1960_1990
GMSL_thermosteric_rcp85=GMSL_thermosteric_rcp85-GMSL_mean1960_1990
        
# Calculate the thickness of temperature layers:
z = Temperature_ocean_lev
Nz = len(z)
zb = np.empty(Nz + 1)
zb[1:-1] = 0.5 * (z[1:] + z[:-1])              # mid-interfaces
zb[0] = 0.0                                    # surface interface
zb[-1] = z[-1] + 0.5 * (z[-1] - z[-2])         # bottom interface guess
Temperature_ocean_dZ = np.diff(zb)


# -----------------------------
# Save variables to be pickled:
# -----------------------------
np.save("Output/to-pickle/sealevel_historical_years.npy", sealevel_historical_years)
np.save("Output/to-pickle/sealevel_historical.npy", sealevel_historical)
np.save("Output/to-pickle/sealevel_rcp85_years.npy", sealevel_rcp85_years)
np.save("Output/to-pickle/sealevel_rcp85.npy", sealevel_rcp85)
np.save("Output/to-pickle/sealevel_lon.npy", sealevel_lon)
np.save("Output/to-pickle/sealevel_lat.npy", sealevel_lat)
np.save("Output/to-pickle/Temperature_ocean_lev.npy", Temperature_ocean_lev)
np.save("Output/to-pickle/Temperature_ocean_dZ.npy", Temperature_ocean_dZ)
np.save("Output/to-pickle/Temperature_ocean_lon.npy", Temperature_ocean_lon)
np.save("Output/to-pickle/Temperature_ocean_lat.npy", Temperature_ocean_lat)
np.save("Output/to-pickle/GMSL_thermosteric_historical.npy", GMSL_thermosteric_historical)
np.save("Output/to-pickle/GMSL_thermosteric_historical_years.npy", GMSL_thermosteric_historical_years)
np.save("Output/to-pickle/GMSL_thermosteric_rcp85.npy", GMSL_thermosteric_rcp85)
np.save("Output/to-pickle/GMSL_thermosteric_rcp85_years.npy", GMSL_thermosteric_rcp85_years)
np.save("Output/to-pickle/Temperature_ocean_1850.npy", Temperature_ocean_1850)
np.save("Output/to-pickle/Temperature_ocean_2100.npy", Temperature_ocean_2100)
