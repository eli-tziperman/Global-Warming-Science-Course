import os
import intake_esgf
import xarray as xr
import numpy as np
import warnings
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

intake_esgf.conf.set(local_cache="~/Downloads/.esgf")
xr.set_options(use_new_combine_kwarg_defaults=True)

# -----------------------------
# CONFIGURATION
# -----------------------------
models = ["HadGEM3-GC31-MM", "GFDL-CM4"]
member_ids = {
    "HadGEM3-GC31-MM": "r1i1p1f3",
    "GFDL-CM4": "r1i1p1f1"
}

experiments = ["historical", "ssp585"]
variables = ["tas", "clt", "rlds", "rldscs", "rsds", "rsdscs"]
months = range(1,13) # months to average over
last_year = 2080 # year to compare to 1850

out_dir = "Output/to-pickle"
os.makedirs(out_dir, exist_ok=True)

# Target years for each experiment
target_years = {
    "historical": (1850, 1870),
    "ssp585": (last_year, last_year+20)
}

# ---------------
# 1° TARGET GRID:
# ---------------
target_lat_1deg = xr.DataArray(np.arange(-90, 91, 1), dims=("lat",), name="lat")
target_lon_1deg = xr.DataArray(np.arange(0, 360, 1), dims=("lon",), name="lon")

def _normalize_lon_0_360(da: xr.DataArray) -> xr.DataArray:
    """Return a copy of da with lon in [0, 360) and sorted ascending."""
    lon = da["lon"]
    # If already 0..360-ish, just sort
    lon_fixed = (lon % 360).astype(lon.dtype)
    da = da.assign_coords(lon=lon_fixed)
    # Sort for interp safety
    return da.sortby("lon")

def regrid_to_1deg(da: xr.DataArray) -> xr.DataArray:
    """Bilinear interpolation to a 1° lat-lon grid."""

    da = _normalize_lon_0_360(da)

    # Interpolate
    da_i = da.interp(lat=target_lat_1deg, lon=target_lon_1deg, method="linear")
    return da_i

# --------------------
# SEARCH ESGF CATALOG:
# --------------------
cat = intake_esgf.ESGFCatalog()
print("Searching ESGF catalog...")

member_list = [member_ids[m] for m in models if m in member_ids]

cat.search(
    project='CMIP6',
    source_id=models,
    variable_id=variables,
    table_id='Amon',
    experiment_id=experiments,
    member_id=member_list,
    type='Dataset',
    quiet=True
)

df = cat.df
print(f"Found {len(df)} dataset entries.")

# --------------
# Load datasets:
# --------------
print("Loading datasets...")
dsets = cat.to_dataset_dict(quiet=True)
print(f"Loaded {len(dsets)} dataset groups.")

# --------------------------------------------------------
# Average over selected months for a given range of years:
# --------------------------------------------------------
def extract_year_mean(da: xr.DataArray, year: int, months_sel=None) -> xr.DataArray:
    """Average over selected months within a given year.

    da : xr.DataArray; Input time series.
    year : int; Year to extract.
    months_sel : list[int] | None
        Months to average over (1-12). If None, uses global `months`.
    """
    if months_sel is None:
        months_sel = months

    t = da.time
    mask = (((t.dt.year >= year[0]) & (t.dt.year <= year[1])) \
            if isinstance(year, (tuple, list, np.ndarray)) \
            else (t.dt.year == year)) & (t.dt.month.isin(months_sel))
    out = da.sel(time=mask).mean(dim="time")
    return out.compute()

# -------------------
# PROCESS EACH MODEL:
# -------------------
for model in models:
    print(f"Processing {model}...")
    results = {}
    hist_data = {}
    ssp_data = {}

    if "HadGEM" in model:
        model_short = "Hadley"
    elif "GFDL-CM4" in model:
        model_short = "GFDL"
    else:
        model_short = model

    for key, ds in dsets.items():
        if model not in key:
            continue

        exp = ds.attrs.get('experiment_id')
        if exp is None:
            exp = 'historical' if 'historical' in key \
                else 'ssp585' if 'ssp585' in key else None
        if exp not in experiments:
            continue

        #print(f"  Processing {exp} dataset: {key}")

        for var in variables:
            if var not in ds.data_vars:
                continue
            da = ds[var]

            # Extract target years and regrid:
            target = target_years[exp]
            arr = extract_year_mean(da, target)
            arr_1deg = regrid_to_1deg(arr)

            if exp == 'historical':
                hist_data[var] = arr_1deg
            else:
                ssp_data[var] = arr_1deg

    # save the 1° grid lat/lon results:
    results[f"model_clouds_latitude"] = target_lat_1deg.values
    results[f"model_clouds_longitude"] = target_lon_1deg.values

    # Compute Deltas on 1° grid
    if "tas" in hist_data and "tas" in ssp_data:
        results[f"Delta_SAT_{model_short}"] \
            = (ssp_data["tas"] - hist_data["tas"]).values
        results[f"Delta_cloud_{model_short}"] \
            = (ssp_data["clt"] - hist_data["clt"]).values
        #print(" Computed Delta_SAT and Delta_cloud (1° grid)")

    if "clt" in hist_data:
        results[f"clouds_{model_short}_historical"] = hist_data["clt"].values
        #print(" Extracted clouds historical (1° grid)")
    if "clt" in ssp_data:
        results[f"clouds_{model_short}_rcp85"] = ssp_data["clt"].values
        #print(" Extracted clouds ssp585 (1° grid)")

    if all(v in hist_data for v in ["rlds", "rldscs"]) \
       and all(v in ssp_data for v in ["rlds", "rldscs"]):
        crf_hist = hist_data["rlds"] - hist_data["rldscs"]
        crf_ssp  = ssp_data["rlds"] - ssp_data["rldscs"]
        results[f"Delta_LW_CRF_{model_short}"] = (crf_ssp - crf_hist).values
        #print(" Computed Delta_LW_CRF (1° grid)")

    if all(v in hist_data for v in ["rsds", "rsdscs"]) \
       and all(v in ssp_data for v in ["rsds", "rsdscs"]):
        crf_hist = hist_data["rsds"] - hist_data["rsdscs"]
        crf_ssp  = ssp_data["rsds"] - ssp_data["rsdscs"]
        results[f"Delta_SW_CRF_{model_short}"] = (crf_ssp - crf_hist).values
        #print(" Computed Delta_SW_CRF (1° grid)")

    # --- Save ---
    for name, arr in results.items():
        out_path = os.path.join(out_dir, f"{name}.npy")
        np.save(out_path, arr)
        #print(f" Saved {name}.npy")

print("Done. Saved npy files to Output/to-pickle/")

# -----
# PLOT:
# -----
data_dir = out_dir
plot_models = ["Hadley", "GFDL"]

lat = np.load(f"{data_dir}/model_clouds_latitude.npy")
lon = np.load(f"{data_dir}/model_clouds_longitude.npy")
d_clt_Hadley = np.load(f"{data_dir}/Delta_cloud_Hadley.npy")
d_clt_GFDL = np.load(f"{data_dir}/Delta_cloud_GFDL.npy")
d_sw_Hadley = np.load(f"{data_dir}/Delta_SW_CRF_Hadley.npy")
d_sw_GFDL = np.load(f"{data_dir}/Delta_SW_CRF_GFDL.npy")
delta_clt_diff = d_clt_Hadley - d_clt_GFDL
delta_sw_diff = d_sw_Hadley - d_sw_GFDL

print("Plotting...")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 3),
                       subplot_kw={'projection': ccrs.PlateCarree()},
                       constrained_layout=True
                       )

# Delta CLT:
ax[0].add_feature(cfeature.COASTLINE, linewidth=0.8)
ax[0].add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
mesh = ax[0].pcolormesh(
    lon, lat, delta_clt_diff,
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r", vmin=-20, vmax=20,
    shading='auto'
)
ax[0].set_title("$\\Delta$CLT: Hadley − GFDL", fontsize=12, pad=10)
plt.colorbar(mesh, ax=ax[0], orientation='vertical', shrink=0.5,
             pad=0.05, label="Cloud fraction (%)")

# Delta SW:
ax[1].add_feature(cfeature.COASTLINE, linewidth=0.5)
ax[1].add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
mesh = ax[1].pcolormesh(
    lon, lat, delta_sw_diff,
    transform=ccrs.PlateCarree(),
    cmap="RdBu", vmin=-30, vmax=30,
    shading='auto'
)
ax[1].set_title("$\\Delta$SW: Hadley − GFDL", fontsize=12, pad=10)
plt.colorbar(mesh, ax=ax[1], orientation='vertical', shrink=0.5,
             pad=0.05, label="W/m$^2$")


plt.savefig("Output/Delta_CLT_SW_Hadley_minus_GFDL.pdf", dpi=300, bbox_inches='tight')
plt.show()
