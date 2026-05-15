import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import subprocess
import os
import glob
from urllib.parse import urlencode
import warnings
warnings.filterwarnings('ignore')

def download_esgf_file(url, filename, max_retries=3):
    """Download file using wget with SSL bypass"""
    
    for attempt in range(max_retries):
        try:
            print(f"  Downloading {filename} (attempt {attempt + 1})...")
            
            # Use wget with SSL bypass
            cmd = [
                'wget', 
                '--no-check-certificate',  # Bypass SSL certificate checks
                '--timeout=60',
                '--tries=3',
                '-O', filename,
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(filename):
                file_size = os.path.getsize(filename)
                if file_size > 1000:  # At least 1KB
                    print(f"    Successfully downloaded {filename} ({file_size/1024/1024:.1f} MB)")
                    return True
                else:
                    print(f"    Downloaded file too small, removing...")
                    os.remove(filename)
            else:
                print(f"    wget failed: {result.stderr}")
                
        except Exception as e:
            print(f"    Download attempt {attempt + 1} failed: {str(e)}")
    
    return False

def search_and_download_damip_data(experiment, data_dir='damip_data', max_files=3):
    """Search ESGF and download real DAMIP data files"""
    
    print(f"\nSearching and downloading {experiment} data...")
    
    # Create data directory
    os.makedirs(data_dir, exist_ok=True)
    
    # ESGF search API
    search_url = "https://esgf-node.llnl.gov/esg-search/search"
    
    params = {
        'offset': 0,
        'limit': 50,
        'type': 'File',
        'format': 'application/solr+json',
        'latest': 'true',
        'activity_id': 'DAMIP',
        'institution_id': 'NCAR',
        'source_id': 'CESM2', 
        'experiment_id': experiment,
        'table_id': 'Amon',
        'variable_id': 'ta',
        'grid_label': 'gn'
    }
    
    try:
        # Search for files
        response = requests.get(search_url, params=params, timeout=30, verify=False)
        response.raise_for_status()
        
        data = response.json()
        
        if 'response' not in data or 'docs' not in data['response']:
            print(f"No files found for {experiment}")
            return []
        
        files = data['response']['docs']
        print(f"Found {len(files)} files")
        
        # Download files
        downloaded_files = []
        file_count = 0
        
        for file_doc in files:
            if file_count >= max_files:
                break
                
            if 'url' in file_doc:
                urls = file_doc['url']
                member_id = file_doc.get('member_id', ['unknown'])[0]
                
                # Find HTTP download URL
                download_url = None
                for url_entry in urls:
                    url_parts = url_entry.split('|')
                    if len(url_parts) >= 2:
                        url = url_parts[0]
                        url_type = url_parts[1]
                        
                        if 'HTTPServer' in url_type or 'http' in url.lower():
                            download_url = url
                            break
                
                if download_url:
                    # Create filename
                    filename = f"{experiment}_{member_id}_{file_count}.nc"
                    filepath = os.path.join(data_dir, filename)
                    
                    # Download file
                    if download_esgf_file(download_url, filepath):
                        downloaded_files.append({
                            'filepath': filepath,
                            'member_id': member_id,
                            'experiment': experiment
                        })
                        file_count += 1
        
        print(f"Successfully downloaded {len(downloaded_files)} files for {experiment}")
        return downloaded_files
        
    except Exception as e:
        print(f"Error searching/downloading {experiment}: {str(e)}")
        return []

def load_and_process_files(file_list):
    """Load and combine downloaded NetCDF files"""
    
    if not file_list:
        return None
    
    print(f"Loading {len(file_list)} files...")
    
    datasets = []
    for file_info in file_list:
        try:
            filepath = file_info['filepath']
            member_id = file_info['member_id']
            
            print(f"  Loading {filepath}...")
            
            # Open dataset
            ds = xr.open_dataset(filepath, chunks={'time': 12})
            
            if 'ta' in ds.data_vars:
                # Add member coordinate
                da = ds['ta'].expand_dims('member').assign_coords(member=[member_id])
                datasets.append(da)
                print(f"    Success: {da.shape}, time range: {da.time.dt.year.min().values}-{da.time.dt.year.max().values}")
            else:
                print(f"    No 'ta' variable found")
                
        except Exception as e:
            print(f"    Error loading {filepath}: {str(e)}")
            continue
    
    if not datasets:
        return None
    
    # Combine datasets
    try:
        combined = xr.concat(datasets, dim='member')
        
        # Sort by time
        combined = combined.sortby('time')
        
        print(f"Combined dataset: {combined.shape}")
        print(f"Time range: {combined.time.dt.year.min().values} to {combined.time.dt.year.max().values}")
        
        return combined
        
    except Exception as e:
        print(f"Error combining datasets: {str(e)}")
        return None

def calculate_temperature_anomaly(da):
    """Calculate zonally-averaged, ensemble-averaged temperature anomaly"""
    
    print("Processing temperature data...")
    
    # Zonal mean
    if 'lon' in da.dims:
        da_zonal = da.mean(dim='lon', skipna=True)
        print(f"After zonal averaging: {da_zonal.shape}")
    else:
        da_zonal = da
    
    # Ensemble mean
    if 'member' in da_zonal.dims and da_zonal.sizes['member'] > 1:
        da_ensemble = da_zonal.mean(dim='member', skipna=True)
        print(f"After ensemble averaging: {da_ensemble.shape}")
    else:
        da_ensemble = da_zonal.squeeze('member') if 'member' in da_zonal.dims else da_zonal
    
    # Calculate decadal anomaly
    years = da_ensemble.time.dt.year
    start_year = int(years.min())
    end_year = int(years.max())
    
    print(f"Data time range: {start_year}-{end_year}")
    
    if (end_year - start_year + 1) < 20:
        print("Insufficient data for decadal comparison")
        return None
    
    # First and last decades
    first_decade_years = list(range(start_year, min(start_year + 10, end_year + 1)))
    last_decade_years = list(range(max(end_year - 9, start_year), end_year + 1))
    
    first_decade = da_ensemble.sel(time=da_ensemble.time.dt.year.isin(first_decade_years))
    last_decade = da_ensemble.sel(time=da_ensemble.time.dt.year.isin(last_decade_years))
    
    first_mean = first_decade.mean(dim='time', skipna=True)
    last_mean = last_decade.mean(dim='time', skipna=True)
    
    anomaly = last_mean - first_mean
    
    print(f"First decade: {min(first_decade_years)}-{max(first_decade_years)}")
    print(f"Last decade: {min(last_decade_years)}-{max(last_decade_years)}")
    print(f"Anomaly range: {float(anomaly.min()):.3f} to {float(anomaly.max()):.3f} K")
    
    return anomaly

def create_fingerprint_plots(anomaly_dict):
    """Create temperature fingerprint plots"""
    
    experiments = ['hist-GHG', 'hist-nat', 'hist-aer']
    available_data = {k: v for k, v in anomaly_dict.items() if v is not None}
    
    if not available_data:
        print("No data available for plotting")
        return
    
    n_plots = len(available_data)
    fig, axes = plt.subplots(1, n_plots, figsize=(6*n_plots, 8))
    if n_plots == 1:
        axes = [axes]
    
    titles = {
        'hist-GHG': 'Greenhouse Gas Forcing',
        'hist-nat': 'Natural Forcing',
        'hist-aer': 'Aerosol Forcing'
    }
    
    # Common color scale
    all_values = []
    for data in available_data.values():
        all_values.extend(data.values.flatten())
    
    vmax = np.percentile(np.abs(all_values), 95)
    levels = np.linspace(-vmax, vmax, 21)
    
    for i, (experiment, anomaly) in enumerate(available_data.items()):
        ax = axes[i]
        
        # Get coordinates
        lat = anomaly.lat.values
        pressure = anomaly.plev.values / 100  # Pa to hPa
        
        # Create meshgrid and plot
        X, Y = np.meshgrid(lat, pressure)
        Z = anomaly.values
        
        cs = ax.contourf(X, Y, Z, levels=levels, cmap='RdBu_r', extend='both')
        ax.contour(X, Y, Z, levels=levels[::2], colors='black', linewidths=0.5, alpha=0.6)
        ax.contour(X, Y, Z, levels=[0], colors='black', linewidths=1.2)
        
        # Formatting
        ax.set_title(titles.get(experiment, experiment), fontsize=14, fontweight='bold')
        ax.set_xlabel('Latitude (°N)', fontsize=12)
        if i == 0:
            ax.set_ylabel('Pressure (hPa)', fontsize=12)
        
        ax.set_yscale('log')
        ax.invert_yaxis()
        ax.set_xlim(-90, 90)
        
        # Pressure ticks
        p_ticks = [1000, 700, 500, 300, 200, 100, 50, 10, 1]
        ax.set_yticks(p_ticks)
        ax.set_yticklabels(p_ticks)
        
        ax.grid(True, alpha=0.3)
        
        # Colorbar
        cbar = plt.colorbar(cs, ax=ax, shrink=0.8)
        cbar.set_label('ΔT (K)', rotation=270, labelpad=15)
    
    plt.suptitle('NCAR CESM2 DAMIP Temperature Fingerprints\n(Real Data: Last Decade - First Decade)', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

def main():
    """Main function to download and process real DAMIP data"""
    
    print("CMIP6 DAMIP Real Data Analysis")
    print("=" * 40)
    print("Downloading real NCAR CESM2 data from ESGF...")
    print("This will download actual NetCDF files to your computer.")
    print()
    
    # Check if wget is available
    try:
        subprocess.run(['wget', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: wget is required but not found.")
        print("Please install wget:")
        print("- Mac: brew install wget")
        print("- Ubuntu/Debian: sudo apt-get install wget")
        print("- Windows: Download from https://gnuwin32.sourceforge.net/packages/wget.htm")
        return
    
    experiments = ['hist-GHG', 'hist-nat', 'hist-aer']
    anomaly_results = {}
    
    # Process each experiment
    for experiment in experiments:
        print(f"\n{'='*50}")
        print(f"Processing {experiment}")
        print(f"{'='*50}")
        
        # Download data
        downloaded_files = search_and_download_damip_data(experiment, max_files=2)
        
        if downloaded_files:
            # Load and process
            combined_data = load_and_process_files(downloaded_files)
            
            if combined_data is not None:
                # Calculate anomaly
                anomaly = calculate_temperature_anomaly(combined_data)
                anomaly_results[experiment] = anomaly
            else:
                anomaly_results[experiment] = None
        else:
            anomaly_results[experiment] = None
    
    # Create plots
    print(f"\n{'='*50}")
    print("Creating plots...")
    create_fingerprint_plots(anomaly_results)
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    successful = sum(1 for v in anomaly_results.values() if v is not None)
    print(f"Successfully processed: {successful}/3 experiments")
    
    for exp, data in anomaly_results.items():
        if data is not None:
            print(f"\n{exp}:")
            print(f"  Shape: {data.shape}")
            print(f"  Global mean anomaly: {float(data.mean()):.3f} K")
            print(f"  Max warming: {float(data.max()):.3f} K")
            print(f"  Max cooling: {float(data.min()):.3f} K")
        else:
            print(f"\n{exp}: Failed to process")
    
    return anomaly_results

if __name__ == "__main__":
    results = main()
