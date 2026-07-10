import os
import glob
import warnings

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from xarray.conventions import SerializationWarning


warnings.filterwarnings('ignore', category=SerializationWarning)

DATA_DIR = os.path.expanduser('~/Downloads/damip_data')
OUTPUT_PATH = os.path.join('Output', 'damip_temperature_fingerprints.pdf')
NPY_OUTPUT_DIR = os.path.join('Output', 'to-pickle')
START_YEAR = 1850
END_YEAR = 2014

EXPERIMENTS = [
    {
        'id': 'historical',
        'title': 'Historical All Forcings',
        'members': ['r11i1p1f1'],
        'output_name': 'hist',
    },
    {
        'id': 'hist-GHG',
        'title': 'Greenhouse Gas Forcing',
        'members': ['r1i1p1f1'],
        'output_name': 'GHG',
    },
    {
        'id': 'hist-nat',
        'title': 'Natural Forcing',
        'members': ['r1i1p1f1'],
        'output_name': 'NAT',
    },
    {
        'id': 'hist-aer',
        'title': 'Aerosol Forcing',
        'members': ['r1i1p1f1', 'r3i1p1f1'],
        'output_name': 'AER',
    },
]


def file_year_span(path):
    with xr.open_dataset(path, decode_times=True) as ds:
        years = ds['ta'].time.dt.year
        return int(years.min()), int(years.max())


def local_temperature_files(experiment):
    records = []
    for member in experiment['members']:
        pattern = os.path.join(DATA_DIR, f"*{experiment['id']}*{member}*.nc")
        records.extend((path, *file_year_span(path)) for path in glob.glob(pattern))

    by_span = {}
    for path, start, end in records:
        if (start, end) not in by_span or os.path.basename(path).startswith('ta_Amon_'):
            by_span[(start, end)] = path

    covered_years = set()
    for start, end in by_span:
        covered_years.update(range(start, end + 1))

    if not all(year in covered_years for year in range(START_YEAR, END_YEAR + 1)):
        span_text = ', '.join(f"{start}-{end}" for start, end in sorted(by_span)) or 'no files'
        raise RuntimeError(
            f"{experiment['id']} {', '.join(experiment['members'])} does not cover "
            f"{START_YEAR}-{END_YEAR}; found {span_text}"
        )

    return [path for _, path in sorted(by_span.items())]


def load_temperature(experiment):
    """Open the air temperature field for one experiment."""

    files = local_temperature_files(experiment)
    print(f"Loading {experiment['id']} {', '.join(experiment['members'])}: {len(files)} file(s)")

    ds = xr.open_mfdataset(files, combine='by_coords', chunks={'time': 12})
    da = ds['ta'].sel(time=slice(f'{START_YEAR}-01-01', f'{END_YEAR}-12-31'))
    print(f"  Shape: {da.shape}; time range: {int(da.time.dt.year.min())}-{int(da.time.dt.year.max())}")
    return da


def calculate_temperature_anomaly(da):
    """Return zonal-mean temperature anomaly: last decade minus first decade."""

    da_zonal = da.mean(dim='lon', skipna=True)
    years = da_zonal.time.dt.year
    start_year = int(years.min())
    end_year = int(years.max())

    first_decade = da_zonal.sel(time=years.isin(range(start_year, start_year + 10)))
    last_decade = da_zonal.sel(time=years.isin(range(end_year - 9, end_year + 1)))
    anomaly = last_decade.mean(dim='time', skipna=True) - first_decade.mean(dim='time', skipna=True)

    print(f"  Anomaly: {start_year}-{start_year + 9} to {end_year - 9}-{end_year}")
    return anomaly


def process_experiment(experiment):
    print(f"\nProcessing {experiment['id']}")
    return calculate_temperature_anomaly(load_temperature(experiment))


def color_levels(anomaly_results):
    values = [
        anomaly.values[np.isfinite(anomaly.values)]
        for anomaly in anomaly_results.values()
    ]
    finite_values = np.concatenate([value for value in values if value.size])
    vmax = np.percentile(np.abs(finite_values), 95)
    return np.linspace(-vmax, vmax, 21)


def load_pi_control_variance():
    variance_path = os.path.join(NPY_OUTPUT_DIR, 'fingerprinting_variance_piControl.npy')
    variance = np.load(variance_path).astype(float)
    variance[(~np.isfinite(variance)) | (variance <= 0)] = np.nan
    np.save(variance_path, variance)
    return variance


def mask_undefined_grid_boxes(anomaly_results):
    variance = load_pi_control_variance()
    defined = np.isfinite(variance)

    for anomaly in anomaly_results.values():
        defined &= np.isfinite(anomaly.values)

    for key, anomaly in anomaly_results.items():
        anomaly_results[key] = anomaly.where(defined)

    print(f"Set {defined.size - defined.sum()} undefined grid boxes to NaN")
    return anomaly_results


def format_lat_pressure_axis(ax, title):
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Latitude (°N)', fontsize=12)
    ax.set_yscale('log')
    ax.invert_yaxis()
    ax.set_xlim(-90, 90)
    ax.set_yticks([1000, 700, 500, 300, 200, 100, 50, 10, 1])
    ax.set_yticklabels([1000, 700, 500, 300, 200, 100, 50, 10, 1])
    ax.grid(True, alpha=0.3)


def plot_field(ax, x_grid, y_grid, field, levels, cmap, title, label, extend='both'):
    contours = ax.contourf(x_grid, y_grid, field, levels=levels, cmap=cmap, extend=extend)
    ax.contour(x_grid, y_grid, field, levels=levels[::2], colors='black', linewidths=0.5, alpha=0.6)
    if np.nanmin(field) < 0 < np.nanmax(field):
        ax.contour(x_grid, y_grid, field, levels=[0], colors='black', linewidths=1.2)
    format_lat_pressure_axis(ax, title)
    plt.colorbar(contours, ax=ax, shrink=0.8).set_label(label, rotation=270, labelpad=15)


def create_fingerprint_plots(anomaly_results, output_path=OUTPUT_PATH):
    """Create and save temperature fingerprint plots."""

    levels = color_levels(anomaly_results)
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.ravel()

    reference = anomaly_results[EXPERIMENTS[0]['id']]
    x_grid, y_grid = np.meshgrid(reference.lat.values, reference.plev.values / 100)

    for ax, experiment in zip(axes, EXPERIMENTS):
        anomaly = anomaly_results[experiment['id']]
        plot_field(
            ax, x_grid, y_grid, anomaly.values, levels, 'RdBu_r',
            experiment['title'], 'ΔT (K)',
        )

    std = np.sqrt(load_pi_control_variance())
    std_levels = np.linspace(0, np.nanpercentile(std, 95), 21)
    plot_field(
        axes[len(EXPERIMENTS)], x_grid, y_grid, std, std_levels, 'viridis',
        'piControl Std. Dev.', 'σ(T) (K)', extend='max',
    )

    axes[-1].axis('off')
    axes[0].set_ylabel('Pressure (hPa)', fontsize=12)
    axes[3].set_ylabel('Pressure (hPa)', fontsize=12)
    plt.suptitle(
        'NCAR CESM2 Temperature Fingerprints and piControl Variability',
        fontsize=16,
        fontweight='bold',
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"\nSaved plot to {output_path}")


def save_plotted_data(anomaly_results, output_dir=NPY_OUTPUT_DIR):
    """Save plotted fields and coordinates as NumPy arrays."""

    os.makedirs(output_dir, exist_ok=True)

    reference = anomaly_results[EXPERIMENTS[0]['id']]
    lat = reference.lat.values
    pressure = reference.plev.values / 100
    delta_p = np.abs(np.gradient(pressure)).reshape(-1, 1)

    np.save(os.path.join(output_dir, 'fingerprinting_lat.npy'), lat)
    np.save(os.path.join(output_dir, 'fingerprinting_pressure.npy'), pressure)
    np.save(os.path.join(output_dir, 'fingerprinting_delta_p.npy'), delta_p)

    for experiment in EXPERIMENTS:
        anomaly = anomaly_results[experiment['id']]
        filename = f"fingerprinting_Delta_T_{experiment['output_name']}.npy"
        np.save(os.path.join(output_dir, filename), anomaly.values)

    print(f"Saved plotted data arrays to {output_dir}")


def main():
    print("CMIP6 Temperature Fingerprint Analysis")
    print("=" * 40)
    print(f"Using data directory: {DATA_DIR}")

    anomaly_results = {
        experiment['id']: process_experiment(experiment)
        for experiment in EXPERIMENTS
    }
    anomaly_results = mask_undefined_grid_boxes(anomaly_results)

    create_fingerprint_plots(anomaly_results)
    save_plotted_data(anomaly_results)
    return anomaly_results


if __name__ == "__main__":
    results = main()
