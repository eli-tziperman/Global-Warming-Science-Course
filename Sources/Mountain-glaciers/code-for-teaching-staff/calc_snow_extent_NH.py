# download snow extent data from the Rutgers University Global Snowlab data:

# Robinson, David A., Estilow, Thomas W., and NOAA CDR Program (2012):
# NOAA Climate Data Record (CDR) of Northern Hemisphere (NH) Snow
# Cover Extent (SCE), Version 1. [indicate subset used]. NOAA National
# Centers for Environmental Information. doi: 10.7289/V5N014G9 [access
# date].

# calculate seasonal time series and plot with linear line fits.
# Written for Eli by Gimini, 202512

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import pandas as pd
import requests
import io
import matplotlib.dates as mdates

plt.rcParams['font.family'] = 'Myriad Pro'
plt.rcParams['font.size'] = 10

# Define the View Limits (Axis)
view_start = pd.Timestamp('1980-01-01')
view_end   = pd.Timestamp('2025-01-01') # Extends to 2025 for the tick mark

# 1. Download and Load Data directly from URL
# -------------------------------------------
url = "https://www.ncei.noaa.gov/data/snow-cover-extent/access/nhsce_v01r01_19661004_20251201.nc"

print(f"Downloading data from NOAA NCEI...\n{url}")
try:
    response = requests.get(url)
    response.raise_for_status() # Check for HTTP errors
    
    # Wrap the content in BytesIO to mimic a file object in memory
    file_content = io.BytesIO(response.content)
    
    # Open dataset from memory
    ds = xr.open_dataset(file_content)
    print("Download complete. Processing data...")

except requests.exceptions.RequestException as e:
    print(f"Error downloading file: {e}")
    exit()

# 2. Calculate Total Snow Area
# ----------------------------
# The NOAA CDR data is usually on an 88x88 Polar Stereographic grid.
# values: 1 = Snow, 0 = No Snow. 
CELL_AREA_KM2 = 25000  # Approximation for Rutgers grid cells
SNOW_FLAG = 1

# Find spatial dimensions (usually y, x or rows, cols)
spatial_dims = [d for d in ds.dims if d != 'time']

# Create a boolean mask for snow and sum it up
snow_pixels = (ds['snow_cover_extent'] == SNOW_FLAG).sum(dim=spatial_dims)

# Convert to Million Square km
total_area_mkm2 = (snow_pixels * CELL_AREA_KM2) / 1e6

# 3. Resample to Seasonal Data
# ----------------------------
# QS-DEC splits data into quarters starting in December (DJF, MAM, JJA, SON)
seasonal_ds = total_area_mkm2.resample(time='QS-DEC').mean(dim='time')

# 4. Plotting
# -----------
seasons = ['DJF', 'MAM', 'JJA', 'SON']
season_names = {
    'DJF': 'Winter (Dec-Feb)',
    'MAM': 'Spring (Mar-May)',
    'JJA': 'Summer (Jun-Aug)',
    'SON': 'Autumn (Sep-Nov)'
}

fig, axes = plt.subplots(2, 2, figsize=(8, 6), sharey=False)
axes = axes.flatten()

#print(f"{'Season':<10} | {'Slope (M km2/yr)':<20} | {'P-Value':<10}")
#print("-" * 50)

start_date = pd.Timestamp('1980-01-01')
end_date = pd.Timestamp('2024-12-31')

# dictionary for data for students:
snow_extent_north_hemisphere={}

for i, season in enumerate(seasons):
    ax = axes[i]
    
    # Access .dt.season directly on the time coordinate
    season_data = seasonal_ds.sel(time=seasonal_ds.time.dt.season == season)
    
    # This ensures the last DATA POINT is from 2024
    season_data = season_data.sel(time=slice('1980-01-01', '2024-12-31'))
    season_data = season_data.dropna(dim='time')
    
    if len(season_data) == 0:
        continue

    # Convert to pandas
    df = season_data.to_dataframe(name='area')
    df = df.reset_index()
    
    # Create Decimal Year for Regression (e.g., 2000.5)
    df['decimal_year'] = df['time'].dt.year + df['time'].dt.dayofyear / 365.25
    
    # Linear Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(df['decimal_year'], df['area'])
    
    # Generate the regression line
    line = slope * df['decimal_year'] + intercept
    
    # add data for students to dictionary:
    time=df['time']
    area=df['area']
    snow_extent_north_hemisphere[season] = {
        'time': time, 
        'area': area
    }
    
    # Plotting
    ax.plot(time, area, label='Snow Extent', color='steelblue', linewidth=1.5)
    ax.plot(time, line, label=f'Trend: ${slope*10:.2f}$ M km$^2/$dec', color='red', linestyle='--')

    # Formatting
    ax.set_title(season_names[season], fontsize=12)#, fontweight='bold')
    ax.set_ylabel('Snow extent ($10^6$ km$^2$)')
    if i==2 or i==3:
        ax.set_xlabel('Year')        
    ax.set_xlim(view_start, view_end)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='best')

    # 2. Major Ticks (The labels with numbers)
    # We set this to every 5 years so the text doesn't overlap, 
    # but it ensures 1980, 1985... 2020, 2025 are hit.
    ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # 3. Minor Ticks (The small ticks without numbers)
    # Set this to 1 year to satisfy your "every year" requirement
    ax.xaxis.set_minor_locator(mdates.YearLocator(1))
    
    # Print stats
    #print(f"{season:<10} | {slope:<20.5f} | {p_value:<10.4f}")

# save data for students
np.save("Output/to-pickle/snow_extent_north_hemisphere.npy",snow_extent_north_hemisphere)
plt.tight_layout()
plt.show()
