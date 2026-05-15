# Read and plot sea level data from tide gauges for several storms.
# https://tidesandcurrents.noaa.gov/peakwaterlevels/
# Eli, 202509

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
import subprocess

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

data_dir="../../../Data-for-teaching-staff/Floods/tide-gauges-data/"
files=[
    data_dir+"CO-OPS_8518750_wl_Sandy_NYC.csv",
    data_dir+"CO-OPS_8410140_wl_Noreaster_Eastport_ME.csv",
    data_dir+"CO-OPS_8665530_wl_Idalia_Charleston_SC.csv",
    data_dir+"CO-OPS_8727520_wl_Idalia_Cedar_Key_FL.csv",
    data_dir+"CO-OPS_8770777_wl_Beryl_Manchester_Houston_TX.csv"
       ]
titles=[
    "(a) Sandy, The Battery, NYC, 2012",
    "(b) Noreaster, Eastport, ME, 2020",
    "(c) Idalia, Charleston, SC, 2023",
    "(d) Idalia, Cedar Key, FL, 2023",
    "(e) Beryl, Houston, TX, 2024"
]
# minor, moderate, major:
flood_thresholds=[
    [0.654,1.035,1.493],
    [1.137,1.442,1.747],
    [0.378,0.530,0.683],
    [0.672,1.218,1.889],
    [0.628,0.872,1.024]
]

# create a list of dictionaries with all data, to be pickeled for students:
tide_gauge_records=[]

for ifile in range(len(files)):
    csv_path = files[ifile]
    print(ifile, csv_path)
    df = pd.read_csv(csv_path, na_values=["-", "--", ""])
    # Normalize header names and reconcile known variants
    df.columns = (
        df.columns.str.replace("\ufeff", "", regex=False)  # strip BOM if present
                  .str.strip()
                  .str.replace(r"\s+", " ", regex=True)
    )

    # Build a single UTC timestamp from Date + Time (GMT)
    df["datetime"] = pd.to_datetime(
        df["Date"].str.cat(df["Time (GMT)"], sep=" "),
        format="%Y/%m/%d %H:%M",
        utc=True,              # treat the input as GMT/UTC
        errors="raise"
    )

    # (optional) drop the originals and set as index
    df = df.drop(columns=["Date", "Time (GMT)"]).set_index("datetime").sort_index()

    # ensure numeric
    for col in ["Predicted (m)", "Verified (m)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure numeric columns (coerce will turn any non-numeric leftovers into NaN)
    for col in ["Predicted (m)", "Verified (m)"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Use datetime as the index and make sure it is sorted
    # Already set earlier; just sort (guard if needed)
    if "datetime" in df.columns:
        df = df.set_index("datetime")
    df = df.sort_index()

    # Create dictionary with data to be pickeled for students:
    tide_gauge_records.append({"title" : titles[ifile],
                        "time" : df.index,
                        "sea-level-observed" : df["Verified (m)"],
                        "sea-level-predicted" : df["Predicted (m)"],
                        "flood-thresholds" : flood_thresholds[ifile]
                        })


# Plots:
# ------

fig, ax = plt.subplots(nrows=len(tide_gauge_records), ncols=1, figsize=(6, 8))
    
for ifile in range(len(tide_gauge_records)):
    # Plot water level, predicted vs observed:
    time=tide_gauge_records[ifile]["time"]
    predicted=tide_gauge_records[ifile]["sea-level-predicted"]
    observed=tide_gauge_records[ifile]["sea-level-observed"]
    ax[ifile].plot(time, predicted, label="Predicted (m)", linewidth=1.0)
    ax[ifile].plot(time, observed, label="Observed (m)", linewidth=1.0)

    # add dash lines for floods thresholds:
    # linestyle (offset, (on, off, on, off, ...))
    thresholds=tide_gauge_records[ifile]["flood-thresholds"]
    ax[ifile].plot(time, predicted*0+thresholds[2], label="_nolegend_", linewidth=0.5, color='red',linestyle=(0, (14, 4))) 
    ax[ifile].plot(time, predicted*0+thresholds[1], label="_nolegend_", linewidth=0.5, color='black',linestyle=(0, (14, 4)))
    ax[ifile].plot(time, predicted*0+thresholds[0], label="_nolegend_", linewidth=0.5, color='gray',linestyle=(0, (14, 4)))

    ax[ifile].set_title(tide_gauge_records[ifile]["title"], loc="left")
    if ifile==len(files)-1:
        ax[ifile].set_xlabel("Time (GMT)")
        ax[ifile].legend()

    ax[ifile].set_ylabel("Sea level (m)")
    ax[ifile].grid(True, alpha=0.3)

    # make every subplot show month/day for each day, no year, no time
    ax[ifile].xaxis.set_major_locator(DayLocator(interval=1))
    ax[ifile].xaxis.set_major_formatter(DateFormatter("%m/%d"))
    ax[ifile].tick_params(axis='x', which='major', labelbottom=True)


plt.tight_layout()
plt.show(block=False)

# save to npy file to be pickeled for students later:
np.save("Output/to-pickle/tide_gauge_records.npy", tide_gauge_records)
