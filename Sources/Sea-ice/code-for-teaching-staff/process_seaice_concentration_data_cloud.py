#!/usr/bin/env python3
"""
read G02202_V5 north/monthly September sea-ice concentration:
- 1979-09
- latest September available

Interpolate from EPSG:3411 (x,y) to lon/lat 0.5°.
Plot two panels (NorthPolarStereo), 60–90N only.
Zeros and NaNs white.
Save CROPPED (60–90N):
  sic_concentration_obs_Sept_1979.npy
  sic_concentration_obs_Sept_YYYY.npy forlast year in data
  sic_concentration_obs_lon.npy
  sic_concentration_obs_lat.npy
"""

from __future__ import annotations
import re
from pathlib import Path

import numpy as np
import requests
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from matplotlib.colors import ListedColormap
import cartopy.crs as ccrs
from pyproj import CRS, Transformer
from scipy.interpolate import RegularGridInterpolator

BASE_URL = "https://noaadata.apps.nsidc.org/NOAA/G02202_V5/north/monthly/"
OUTDIR = Path("./Output/to-pickle/")
DATADIR=Path("./Output/")

def list_files() -> dict[int, str]:
    html = requests.get(BASE_URL, timeout=60).text
    pat = re.compile(r'href="(sic_psn25_(\d{6})_[^"]+?\.nc)"', re.IGNORECASE)
    return {int(yyyymm): fname for fname, yyyymm in pat.findall(html)}


def download(fname: str) -> Path:
    p = DATADIR / fname
    if p.exists() and p.stat().st_size > 0:
        return p
    with requests.get(BASE_URL + fname, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(p, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
    return p


def read_xy_sic(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ds = xr.open_dataset(path, mask_and_scale=True, decode_cf=True)
    x = ds["x"].values.astype(np.float64)  # meters
    y = ds["y"].values.astype(np.float64)  # meters
    sic = ds["cdr_seaice_conc_monthly"].isel(time=0).values.astype(np.float64)  # already scaled to 0..1

    # make x,y increasing for RegularGridInterpolator((y,x), sic)
    if x[1] < x[0]:
        x = x[::-1]
        sic = sic[:, ::-1]
    if y[1] < y[0]:
        y = y[::-1]
        sic = sic[::-1, :]

    return x, y, sic


def interp_to_lonlat(x_m, y_m, z_yx, lon_1d, lat_1d) -> np.ndarray:
    itp = RegularGridInterpolator((y_m, x_m), z_yx, bounds_error=False, fill_value=np.nan)
    Lon, Lat = np.meshgrid(lon_1d, lat_1d)
    tf = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(3411), always_xy=True)
    X, Y = tf.transform(Lon, Lat)
    return itp(np.column_stack([Y.ravel(), X.ravel()])).reshape(Lat.shape)


def edges(c: np.ndarray) -> np.ndarray:
    dc = np.diff(c)
    e = np.empty(c.size + 1, dtype=np.float64)
    e[1:-1] = 0.5 * (c[:-1] + c[1:])
    e[0] = c[0] - 0.5 * dc[0]
    e[-1] = c[-1] + 0.5 * dc[-1]
    return e


def plot_two_polar(lon, lat, a, b, year_last: int) -> None:
    pc, proj = ccrs.PlateCarree(), ccrs.NorthPolarStereo()
    lon_e, lat_e = edges(lon), edges(lat)
    white = ListedColormap(["white"])

    fig, axs = plt.subplots(1, 2, figsize=(12, 6),
                            subplot_kw={"projection": proj},
                            constrained_layout=True)

    pms = []
    for ax, data, title in [
        (axs[0], a, "Sea-ice concentration (Sep 1979)"),
        (axs[1], b, f"Sea-ice concentration (Sep {year_last})"),
    ]:
        ax.set_extent([-180, 180, 60, 90], crs=pc)

        pos = np.isfinite(data) & (data > 0)
        pm = ax.pcolormesh(lon_e, lat_e, np.ma.masked_where(~pos, data),
                           transform=pc, cmap="viridis",
                           vmin=0, vmax=1, shading="flat", zorder=1)
        ax.pcolormesh(lon_e, lat_e, np.ma.masked_where(pos, np.ones_like(data)),
                      transform=pc, cmap=white, shading="flat", zorder=2)

        ax.coastlines("110m", linewidth=0.8, zorder=3)
        ax.set_title(title)

        th = np.linspace(0, 2*np.pi, 200)
        ax.set_boundary(mpath.Path(np.vstack([np.sin(th), np.cos(th)]).T * 0.5 + [0.5, 0.5]),
                        transform=ax.transAxes)

        pms.append(pm)

    cb = fig.colorbar(pms[0], ax=axs, shrink=0.9, pad=0.02)
    cb.set_label("Sea-ice concentration (0–1)")
    plt.pause(1.0)
 

def main() -> None:
    files = list_files()
    if 197909 not in files:
        raise RuntimeError("Sep 1979 file not found in directory listing.")
    yyyymm_last = max(k for k in files if k % 100 == 9)
    year_last = yyyymm_last // 100

    p79 = download(files[197909])
    pL = download(files[yyyymm_last])
    print("1979:", p79.name)
    print("last:", pL.name)

    lon = np.arange(-180.0, 180.0, 0.25)     # -180 .. 179.5
    lat = np.arange(0.0, 90.0 + 0.25, 0.25)   # 0 .. 90

    x79, y79, z79 = read_xy_sic(p79)
    xL,  yL,  zL  = read_xy_sic(pL)

    sic79 = interp_to_lonlat(x79, y79, z79, lon, lat)
    sicL  = interp_to_lonlat(xL,  yL,  zL,  lon, lat)

    m = (lat >= 60.0) & (lat <= 90.0)
    lat60 = lat[m]
    sic79_60 = sic79[m, :]
    sicL_60  = sicL[m, :]

    plot_two_polar(lon, lat60, sic79_60, sicL_60, year_last)

    np.save(OUTDIR / "sic_concentration_obs_lon", lon.astype(np.float32))
    np.save(OUTDIR / "sic_concentration_obs_lat", lat60.astype(np.float32))
    np.save(OUTDIR / "sic_concentration_obs_Sept_1979", sic79_60.astype(np.float32))
    np.save(OUTDIR / f"sic_concentration_obs_Sept_{year_last}", sicL_60.astype(np.float32))


if __name__ == "__main__":
    main()
