#!/usr/bin/env python3
"""
read Pangeo CMIP6 Zarr via intake-esm:
  GFDL-ESM4 / ssp585 / Omon / msftyz / gn / r1i1p1f1/ atlantic_arctic_ocean

plot and then output:
  - rcp85_depth.npy
  - rcp85_latitude.npy
  - rcp85_AMOC_first_decade.npy
  - rcp85_AMOC_last_decade.npy
  - rcp85_years.npy
  - rcp85_AMOC_timeseries.npy
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import intake

CATALOG = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"
QUERY = dict(source_id="GFDL-ESM4", experiment_id="ssp585", table_id="Omon",
             variable_id="msftyz", member_id="r1i1p1f1", grid_label="gn")
REGION = "atlantic_arctic_ocean"

RHO0 = 1026.0
FILL = 1e20
LEVELS = np.arange(-8, 30, 2)
LAT_MIN, LAT_MAX = 30.0, 70.0
DEPTH_MIN, DEPTH_MAX = 500.0, 2000.0

outdir = Path(__file__).resolve().parent / "Output/to-pickle"
outdir.mkdir(exist_ok=True)

time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
ds = list(intake.open_esm_datastore(CATALOG)
          .search(**QUERY)
          .to_dataset_dict(xarray_open_kwargs=dict(engine="zarr", consolidated=True, chunks=None,
                                                  decode_times=time_coder))
          .values())[0]

basin = [s.decode().strip() for s in ds["region"].values].index(REGION)
da = ds["msftyz"].isel(basin=basin).squeeze(drop=True)
da = da.where(da != FILL) / (RHO0 * 1e6)  # Sv

y = ds["y"].values
lev = ds["lev"].values

n = da.sizes["time"]
i0 = slice(0, min(120, n))
i1 = slice(max(0, n - min(120, n)), n)
m0 = da.isel(time=i0).mean("time", skipna=True).transpose("lev", "y").compute()
m1 = da.isel(time=i1).mean("time", skipna=True).transpose("lev", "y").compute()

np.save(outdir / "rcp85_depth.npy", lev)
np.save(outdir / "rcp85_latitude.npy", y)
np.save(outdir / "rcp85_AMOC_first_decade.npy", m0.values)
np.save(outdir / "rcp85_AMOC_last_decade.npy", m1.values)

fig, ax = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
c0 = ax[0].contourf(y, lev, m0.values, levels=LEVELS)
c1 = ax[1].contourf(y, lev, m1.values, levels=LEVELS)
for a, t in zip(ax, ["AMOC first decade", "AMOC last decade"]):
    a.invert_yaxis()
    a.set_xlabel("latitude (deg)")
    a.set_ylabel("depth (m)")
    a.set_title(t)
fig.colorbar(c0, ax=ax[0]).set_label("Sv")
fig.colorbar(c1, ax=ax[1]).set_label("Sv")
fig.savefig("Output/AMOC_first_last_decade_contours.pdf")
plt.show()
plt.close(fig)

da_ts = da.sel(y=slice(LAT_MIN, LAT_MAX), lev=slice(DEPTH_MIN, DEPTH_MAX))
amoc = da_ts.max(dim=["lev", "y"], skipna=True).compute().values.reshape(-1)
t = da_ts["time"]
years = (t.dt.year + (t.dt.month - 1) / 12.0).values.astype(float)

np.save(outdir / "rcp85_years.npy", years)
np.save(outdir / "rcp85_AMOC_timeseries.npy", amoc)

fig = plt.figure(figsize=(12, 5))
plt.plot(years, amoc)
plt.xlabel("year")
plt.ylabel("Sv")
plt.title(f"max AMOC time series ({REGION})")
plt.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig("Output/AMOC_timeseries.pdf")
plt.show()
plt.close(fig)

print("Saved outputs under:", outdir)
