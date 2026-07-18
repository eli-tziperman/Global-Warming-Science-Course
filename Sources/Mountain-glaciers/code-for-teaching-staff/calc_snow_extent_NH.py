# Calculate seasonal Northern Hemisphere snow-covered-area anomalies from
# AVHRR10C1.V4 fractional snow cover.
#
# Xiao, X., Naegeli, K., Premier, V., Li, S., Neuhaus, C., Wiesmann, A.,
# and Wunderle, S. (2026). Introduction to a 45-year (1979-2023) global
# daily snow cover fraction product from multiple AVHRR satellites with
# accuracy assessment. Remote Sensing of Environment, 334, 115235.
# https://doi.org/10.1016/j.rse.2026.115235
#
# Data:
# Xiao, X., Naegeli, K., Premier, V., Li, S., Neuhaus, C., and Wunderle, S.
# (2025). A 45-year (1979-2023) Global Daily Snow Cover Fraction Climate Data
# Record from multiple AVHRR satellites (AVHRR10C1.V4).
# https://doi.org/10.5281/zenodo.16746237

from pathlib import Path
import os
import re
import subprocess
import time

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
import requests
from scipy import stats
import xarray as xr


plt.rcParams["font.family"] = "Myriad Pro"
plt.rcParams["font.size"] = 10

START_DATE = pd.Timestamp("1979-01-01")
END_DATE = pd.Timestamp("2023-12-31")

OUTPUT_DIR = Path("Output/to-pickle")
SEASONAL_FIGURE = Path("Output/snow-cover-seasonal-timeseries.pdf")
MONTHLY_FIGURE = Path("Output/snow-cover-monthly-timeseries.pdf")
MARCH_FIGURE = Path("Output/snow-cover-march-scfg-anomaly-xiao17a-aspect.pdf")

DATA_DIR = Path.home() / "Downloads" / "snow-cover-data"
ARCHIVE_DIR = DATA_DIR / "archives"
GEOTIFF_DIR = DATA_DIR / "AVHRR10C1_V4"
PROCESSING_VERSION = "xiao_fig17a_era5land_0p1_v1"
MONTHLY_AREA_CACHE = DATA_DIR / f"monthly_nh_scfg_area_{PROCESSING_VERSION}_mkm2.csv"
TIFF_INDEX_CACHE = DATA_DIR / "avhrr10c1_v4_scfg_tiff_index_1979_2023.csv"
ERA5_LAND_MASK_SOURCE = DATA_DIR / "era5_land_snow_cover_197903_mask_source.nc"

ZENODO_RECORD_API = "https://zenodo.org/api/records/16746237"
REQUEST_TIMEOUT = 60
DOWNLOAD_RETRIES = 3
EARTH_RADIUS_KM = 6371.0088
ERA5_GRID_SPACING_DEGREES = 0.1
MIN_VALID_OBSERVATIONS_PER_PIXEL = 5
XIAO_FIG17A_PANEL_ASPECT = 1010 / 487
XIAO_FIG17A_XLIM = (pd.Timestamp("1976-12-17 10:48:00"), pd.Timestamp("2025-05-12 13:12:00"))
XIAO_FIG17A_YLIM = (-7, 7)


def log(message):
    print(message, flush=True)


def download_file(url, destination, expected_size=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial_destination = destination.with_suffix(destination.suffix + ".part")

    if destination.exists() and (expected_size is None or destination.stat().st_size == expected_size):
        log(f"Using existing file: {destination}")
        return

    if partial_destination.exists():
        partial_destination.unlink()

    last_error = None
    for attempt in range(1, DOWNLOAD_RETRIES + 1):
        try:
            with requests.get(url, stream=True, timeout=REQUEST_TIMEOUT) as response:
                response.raise_for_status()
                with open(partial_destination, "wb") as output:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            output.write(chunk)
            partial_destination.replace(destination)
            return
        except requests.exceptions.RequestException as error:
            last_error = error
            if attempt < DOWNLOAD_RETRIES:
                wait_seconds = 2 ** (attempt - 1)
                log(f"Download failed ({error}); retrying in {wait_seconds} s...")
                time.sleep(wait_seconds)

    raise last_error


def zenodo_files():
    response = requests.get(ZENODO_RECORD_API, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return {item["key"]: item for item in response.json()["files"]}


def download_and_extract_archives():
    archive_names = ["1979-1989.7z", "1990-1999.7z", "2000-2009.7z", "2010-2023.7z"]
    missing_data_path = DATA_DIR / "Dates List of Missing Data.xlsx"

    if all((GEOTIFF_DIR / f".{name}.extracted").exists() for name in archive_names) and missing_data_path.exists():
        log("All AVHRR archives are already extracted; no download is needed.")
        return

    files = zenodo_files()

    for archive_name in archive_names:
        marker_path = GEOTIFF_DIR / f".{archive_name}.extracted"
        if marker_path.exists():
            log(f"Already extracted; skipping archive download: {archive_name}")
            continue

        archive = files[archive_name]
        archive_path = ARCHIVE_DIR / archive_name
        log(f"Archive {archive_name} ({archive['size'] / 1e9:.1f} GB)")
        download_file(archive["links"]["self"], archive_path, expected_size=archive["size"])

        GEOTIFF_DIR.mkdir(parents=True, exist_ok=True)
        log(f"Extracting {archive_name} to {GEOTIFF_DIR}")
        subprocess.run(["bsdtar", "-xf", str(archive_path), "-C", str(GEOTIFF_DIR)], check=True)
        marker_path.write_text("ok\n")

    missing_file = files.get("Dates List of Missing Data.xlsx")
    if missing_file is not None and not missing_data_path.exists():
        download_file(
            missing_file["links"]["self"],
            missing_data_path,
            expected_size=missing_file["size"],
        )


def date_from_name(path):
    if match := re.search(r"(?:19|20)\d{6}", path.name):
        return pd.to_datetime(match.group(0), format="%Y%m%d")
    return None


def build_tiff_index():
    if TIFF_INDEX_CACHE.exists():
        tiff_index = pd.read_csv(TIFF_INDEX_CACHE, parse_dates=["time"])
        if not tiff_index.empty and tiff_index["path"].map(lambda p: Path(p).exists()).all():
            log(f"Using cached GeoTIFF index: {TIFF_INDEX_CACHE}")
            return tiff_index

    log(f"Indexing SCFG GeoTIFF files under {GEOTIFF_DIR}")
    rows = []
    for path in GEOTIFF_DIR.rglob("*.tif*"):
        file_date = date_from_name(path)
        if "SCFG" in path.name.upper() and file_date is not None and START_DATE <= file_date <= END_DATE:
            rows.append({"time": file_date, "path": str(path)})

    tiff_index = pd.DataFrame(rows).sort_values("time")
    if tiff_index.empty:
        raise RuntimeError(f"No SCFG GeoTIFF files found under {GEOTIFF_DIR}")

    TIFF_INDEX_CACHE.parent.mkdir(parents=True, exist_ok=True)
    tiff_index.to_csv(TIFF_INDEX_CACHE, index=False)
    log(f"Indexed {len(tiff_index)} SCFG GeoTIFF files: {TIFF_INDEX_CACHE}")
    return tiff_index


def era5_land_northern_hemisphere_mask():
    """Return the ERA5-Land valid-land mask on 90N..0N, -180..179.9."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not ERA5_LAND_MASK_SOURCE.exists():
        log(f"Downloading ERA5-Land mask source: {ERA5_LAND_MASK_SOURCE}")
        try:
            import cdsapi
        except ImportError as error:
            raise RuntimeError(
                "cdsapi is required to download the ERA5-Land mask source. Install cdsapi and configure ~/.cdsapirc."
            ) from error

        partial_path = ERA5_LAND_MASK_SOURCE.with_suffix(ERA5_LAND_MASK_SOURCE.suffix + ".part")
        if partial_path.exists():
            partial_path.unlink()

        cdsapi.Client().retrieve(
            "reanalysis-era5-land-monthly-means",
            {
                "product_type": "monthly_averaged_reanalysis",
                "variable": ["snow_cover"],
                "year": ["1979"],
                "month": ["03"],
                "time": ["00:00"],
                "data_format": "netcdf",
                "download_format": "unarchived",
            },
            str(partial_path),
        )
        partial_path.replace(ERA5_LAND_MASK_SOURCE)

    with xr.open_dataset(ERA5_LAND_MASK_SOURCE) as era5_ds:
        snow_cover = era5_ds["snowc"].squeeze(drop=True)
        latitude = np.asarray(snow_cover["latitude"])
        longitude = np.asarray(snow_cover["longitude"])
        expected_latitude = np.linspace(90.0, -90.0, 1801)
        expected_longitude = np.arange(3600) * ERA5_GRID_SPACING_DEGREES
        if (
            latitude.shape != expected_latitude.shape
            or longitude.shape != expected_longitude.shape
            or not np.allclose(latitude, expected_latitude)
            or not np.allclose(longitude, expected_longitude)
        ):
            raise RuntimeError(
                "Unexpected ERA5-Land grid; expected latitude 90..-90 and longitude 0..359.9 at 0.1 degrees"
            )

        mask_zero_to_360 = np.isfinite(np.asarray(snow_cover))[:901, :]

    # Put longitude in -180..179.9 order, matching the AVHRR raster.
    mask_minus180_to_180 = np.roll(mask_zero_to_360, 1800, axis=1)
    log(
        "Using ERA5-Land valid-land mask: "
        f"{mask_minus180_to_180.sum():,} of {mask_minus180_to_180.size:,} Northern Hemisphere cells"
    )
    return mask_minus180_to_180


def era5_land_northern_hemisphere_row_areas():
    """Area of one 0.1-degree longitude cell in each ERA5-Land NH row."""
    latitude_centers = np.arange(90.0, -0.01, -ERA5_GRID_SPACING_DEGREES)
    north_edges = np.minimum(90.0, latitude_centers + ERA5_GRID_SPACING_DEGREES / 2)
    south_edges = latitude_centers - ERA5_GRID_SPACING_DEGREES / 2
    lon_width = np.deg2rad(ERA5_GRID_SPACING_DEGREES)
    return EARTH_RADIUS_KM**2 * np.abs(np.sin(np.deg2rad(north_edges)) - np.sin(np.deg2rad(south_edges))) * lon_width


def read_northern_hemisphere_scfg(path):
    with Image.open(path) as image:
        data = np.asarray(image)
    if data.shape != (3600, 7200):
        raise RuntimeError(f"Unexpected AVHRR grid shape {data.shape} in {path}")
    # Include the first Southern Hemisphere row so the ERA5-Land cell
    # centered on 0 degrees can average source pixels centered at +/-0.025.
    return data[:1801]


def aggregate_scfg_to_era5_land(monthly_scfg_fraction, valid, era5_land_mask):
    """Average 0.05-degree AVHRR cells within aligned 0.1-degree ERA5 cells."""
    if monthly_scfg_fraction.shape != (1801, 7200) or valid.shape != monthly_scfg_fraction.shape:
        raise RuntimeError(
            f"Expected matching AVHRR arrays with shape (1801, 7200), got {monthly_scfg_fraction.shape} and {valid.shape}"
        )
    if era5_land_mask.shape != (901, 3600):
        raise RuntimeError(f"Expected ERA5-Land NH mask shape (901, 3600), got {era5_land_mask.shape}")

    # ERA5 longitude 0.0 is centered on the AVHRR pixels at -0.025 and
    # +0.025 degrees. Rolling puts the dateline pair first on a -180..179.9
    # target grid; each subsequent adjacent pair is centered on 0.1 degrees.
    scfg = np.roll(monthly_scfg_fraction, 1, axis=1)
    source_valid = np.roll(valid, 1, axis=1)

    coarse_sum = np.zeros((901, 3600), dtype=np.float32)
    coarse_count = np.zeros((901, 3600), dtype=np.uint8)

    # The 90-degree ERA5 row is a half cell and has no valid ERA5-Land
    # points, but populate it consistently from the single AVHRR latitude row.
    coarse_sum[0] = scfg[0, 0::2] + scfg[0, 1::2]
    coarse_count[0] = source_valid[0, 0::2] + source_valid[0, 1::2]

    coarse_sum[1:] = scfg[1:].reshape(900, 2, 3600, 2).sum(axis=(1, 3))
    coarse_count[1:] = source_valid[1:].reshape(900, 2, 3600, 2).sum(axis=(1, 3))

    coarse_scfg_fraction = np.divide(
        coarse_sum,
        coarse_count,
        out=np.zeros_like(coarse_sum),
        where=coarse_count > 0,
    )
    comparison_domain = era5_land_mask & (coarse_count > 0)
    return coarse_scfg_fraction, comparison_domain


def snow_area_from_month_files(paths, era5_land_mask):
    if len(paths) < MIN_VALID_OBSERVATIONS_PER_PIXEL:
        return np.nan, 0.0

    scfg_sum = np.zeros((1801, 7200), dtype=np.float32)
    valid_count = np.zeros((1801, 7200), dtype=np.uint16)

    for path in paths:
        nh_data = read_northern_hemisphere_scfg(path)
        valid = (nh_data >= 0) & (nh_data <= 100)

        scfg_sum += np.where(valid, nh_data, 0).astype(np.float32)
        valid_count += valid

    enough_observations = valid_count >= MIN_VALID_OBSERVATIONS_PER_PIXEL
    monthly_scfg_fraction = np.divide(
        scfg_sum,
        valid_count * 100.0,
        out=np.zeros_like(scfg_sum, dtype=np.float32),
        where=enough_observations,
    )

    coarse_scfg_fraction, comparison_domain = aggregate_scfg_to_era5_land(
        monthly_scfg_fraction, enough_observations, era5_land_mask
    )
    row_areas = era5_land_northern_hemisphere_row_areas()
    valid_area_mkm2 = float(np.dot(comparison_domain.sum(axis=1), row_areas) / 1e6)
    if valid_area_mkm2 == 0.0:
        return np.nan, 0.0

    masked_scfg_fraction = np.where(comparison_domain, coarse_scfg_fraction, 0.0)
    snow_area_mkm2 = float(np.dot(masked_scfg_fraction.sum(axis=1), row_areas) / 1e6)
    return snow_area_mkm2, valid_area_mkm2


def build_monthly_area_series(tiff_index, era5_land_mask):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tiff_index = tiff_index.assign(month=tiff_index["time"].dt.to_period("M").dt.to_timestamp())

    if MONTHLY_AREA_CACHE.exists():
        monthly_area = pd.read_csv(
            MONTHLY_AREA_CACHE, parse_dates=["time"], usecols=["time", "area", "valid_area", "daily_files"]
        )
        completed_months = set(monthly_area["time"])
        log(f"Loaded {len(monthly_area)} cached monthly areas from {MONTHLY_AREA_CACHE}")
    else:
        monthly_area = pd.DataFrame(columns=["time", "area", "valid_area", "daily_files"])
        completed_months = set()
        log(f"New monthly cache will be written to {MONTHLY_AREA_CACHE}")

    remaining = [
        (month, group) for month, group in tiff_index.groupby("month", sort=True) if month not in completed_months
    ]
    max_months = os.environ.get("SNOW_CCI_MAX_MONTHS")
    if max_months:
        remaining = remaining[: int(max_months)]

    if not remaining:
        log("All indexed months are already cached.")
        return monthly_area.sort_values("time")

    log(f"Processing {len(remaining)} AVHRR10C1.V4 monthly SCFG fields")
    log(
        "For each pixel, monthly SCFG is the mean of valid daily values "
        f"when at least {MIN_VALID_OBSERVATIONS_PER_PIXEL} valid observations exist"
    )
    new_rows = []
    run_start = time.perf_counter()

    def save_new_rows():
        nonlocal monthly_area, new_rows
        if not new_rows:
            return
        new_monthly_area = pd.DataFrame(new_rows)
        monthly_area = (
            new_monthly_area
            if monthly_area.empty
            else pd.concat([monthly_area, new_monthly_area], ignore_index=True)
        )
        monthly_area.sort_values("time", inplace=True)
        monthly_area.to_csv(MONTHLY_AREA_CACHE, index=False)
        log(f"    saved {len(monthly_area)} cached monthly areas to {MONTHLY_AREA_CACHE}")
        new_rows.clear()

    for n, (month, group) in enumerate(remaining, start=1):
        month_start = time.perf_counter()
        paths = group.sort_values("time")["path"].tolist()
        area, valid_area = snow_area_from_month_files(paths, era5_land_mask)
        new_rows.append(
            {
                "time": month,
                "area": area,
                "valid_area": valid_area,
                "daily_files": len(paths),
            }
        )

        elapsed = time.perf_counter() - run_start
        eta_hours = elapsed / n * (len(remaining) - n) / 3600
        log(
            f"{n:4d}/{len(remaining):4d}: {month.date()} "
            f"area={area:.3f} M km2; valid={valid_area:.1f} M km2; "
            f"files={len(paths)}; month={time.perf_counter() - month_start:.1f} s; ETA={eta_hours:.1f} h"
        )

        if n % 12 == 0:
            save_new_rows()

    save_new_rows()
    return monthly_area.sort_values("time")


def monthly_area_dataarray(monthly_area):
    return xr.DataArray(monthly_area["area"], coords={"time": pd.to_datetime(monthly_area["time"])}, dims="time")


def anomaly_dataframe(data):
    """Return area, anomaly, and linear trend columns for a time series."""
    frame = pd.DataFrame({"time": pd.to_datetime(data["time"].to_numpy()), "area": data.to_numpy()})
    frame["anomaly"] = frame["area"] - frame["area"].mean()
    frame["decimal_year"] = frame["time"].dt.year + frame["time"].dt.dayofyear / 365.25
    regression = stats.linregress(frame["decimal_year"], frame["anomaly"])
    frame["trend"] = regression.slope * frame["decimal_year"] + regression.intercept
    return frame, regression


def plot_anomaly_lines(ax, frame, data_label, trend_label, color="steelblue", linewidth=1.2):
    ax.plot(frame["time"], frame["anomaly"], label=data_label, color=color, linewidth=linewidth)
    ax.plot(frame["time"], frame["trend"], label=trend_label, color="red", linestyle="--", linewidth=linewidth)


def format_year_axis(ax):
    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.YearLocator(1))


def finish_figure(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf")
    plt.close(fig)
    log(f"Saved figure: {path}")


def plot_seasonal_anomalies(monthly_area):
    total_area_mkm2 = monthly_area_dataarray(monthly_area)

    seasonal_ds = total_area_mkm2.resample(time="QS-DEC").mean(dim="time")
    seasonal_counts = total_area_mkm2.resample(time="QS-DEC").count(dim="time")

    season_names = {
        "DJF": "Winter (Dec-Feb)",
        "MAM": "Spring (Mar-May)",
        "JJA": "Summer (Jun-Aug)",
        "SON": "Autumn (Sep-Nov)",
    }

    fig, axes = plt.subplots(2, 2, figsize=(8, 6))
    snow_area_north_hemisphere = {}

    for i, (ax, (season, season_name)) in enumerate(zip(axes.flat, season_names.items())):
        season_data = seasonal_ds.sel(time=seasonal_ds.time.dt.season == season)
        season_count = seasonal_counts.sel(time=seasonal_counts.time.dt.season == season)
        season_data = season_data.sel(time=slice(START_DATE, END_DATE))
        season_count = season_count.sel(time=slice(START_DATE, END_DATE))
        season_data = season_data.where(season_count == 3).dropna(dim="time")

        if season_data.size == 0:
            continue

        df, regression = anomaly_dataframe(season_data)
        snow_area_north_hemisphere[season] = {name: df[name] for name in ("time", "area", "anomaly")}
        plot_anomaly_lines(
            ax,
            df,
            "SCFG SCA anomaly",
            f"Trend: ${regression.slope * 10:.2f}$ M km$^2/$dec",
            linewidth=1.5,
        )
        ax.set_title(season_name, fontsize=12)
        ax.set_ylabel("SCA anomaly ($10^6$ km$^2$)")
        if i in (2, 3):
            ax.set_xlabel("Year")
        ax.set_xlim(START_DATE, pd.Timestamp("2025-01-01"))
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="best")
        format_year_axis(ax)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    np.save(OUTPUT_DIR / "snow_extent_north_hemisphere.npy", snow_area_north_hemisphere)

    fig.tight_layout()
    finish_figure(fig, SEASONAL_FIGURE)


def plot_monthly_anomalies(monthly_area):
    monthly_ds = monthly_area_dataarray(monthly_area)
    month_names = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

    fig, axes = plt.subplots(4, 3, figsize=(9, 10), sharex=True)
    monthly_snow_area = {}

    for month, ax in enumerate(axes.flat, start=1):
        month_data = monthly_ds.sel(time=monthly_ds.time.dt.month == month).sel(time=slice(START_DATE, END_DATE))
        month_data = month_data.dropna("time")

        if month_data.size == 0:
            ax.set_title(month_names[month - 1], fontsize=11)
            continue

        df, regression = anomaly_dataframe(month_data)

        monthly_snow_area[month_names[month - 1]] = {name: df[name] for name in ("time", "area", "anomaly")}
        plot_anomaly_lines(
            ax,
            df,
            "SCFG SCA anomaly",
            f"{regression.slope * 10:.2f} M km$^2$/dec; $R^2={regression.rvalue**2:.2f}$",
        )
        ax.axhline(0, color="0.6", linewidth=0.8, linestyle=":")
        ax.set_title(month_names[month - 1], fontsize=11)
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="best", fontsize=8)
        if month in (1, 4, 7, 10):
            ax.set_ylabel("SCA anomaly\n($10^6$ km$^2$)")
        if month >= 10:
            ax.set_xlabel("Year")
        format_year_axis(ax)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    np.save(OUTPUT_DIR / "snow_area_monthly_north_hemisphere.npy", monthly_snow_area)

    fig.tight_layout()
    finish_figure(fig, MONTHLY_FIGURE)


def plot_march_anomaly_xiao_style(monthly_area):
    monthly_ds = monthly_area_dataarray(monthly_area)
    march_data = monthly_ds.sel(time=monthly_ds.time.dt.month == 3).sel(time=slice(START_DATE, END_DATE)).dropna("time")

    if march_data.size == 0:
        raise RuntimeError("No March AVHRR10C1.V4 SCFG monthly areas are available to plot.")

    df, regression = anomaly_dataframe(march_data)

    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_box_aspect(1 / XIAO_FIG17A_PANEL_ASPECT)
    plot_anomaly_lines(
        ax,
        df,
        "AVHRR10C1.V4 SCFG",
        f"Trend: {regression.slope * 10:.2f} M km$^2$/dec",
        color="tab:orange",
        linewidth=1.6,
    )
    ax.axhline(0, color="0.55", linewidth=0.8, linestyle=":")
    ax.set_title("March")
    ax.set_ylabel("SCA anomaly ($10^6$ km$^2$)")
    ax.set_xlabel("Year")
    ax.set_xlim(*XIAO_FIG17A_XLIM)
    ax.set_ylim(*XIAO_FIG17A_YLIM)
    ax.set_yticks(np.arange(-6, 7, 2))
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="best")
    format_year_axis(ax)

    fig.tight_layout()
    finish_figure(fig, MARCH_FIGURE)


def main():
    era5_land_mask = era5_land_northern_hemisphere_mask()
    download_and_extract_archives()
    tiff_index = build_tiff_index()
    monthly_area = build_monthly_area_series(tiff_index, era5_land_mask)

    if monthly_area.empty:
        raise RuntimeError("No AVHRR10C1.V4 SCFG monthly fields were processed.")

    plot_seasonal_anomalies(monthly_area)
    plot_monthly_anomalies(monthly_area)
    plot_march_anomaly_xiao_style(monthly_area)


if __name__ == "__main__":
    main()
