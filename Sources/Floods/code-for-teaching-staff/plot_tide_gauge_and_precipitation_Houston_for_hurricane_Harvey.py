# plot both precipitation and water level for Hurricane Harvey, Houston 2017

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
import subprocess
from matplotlib.ticker import MultipleLocator, NullFormatter
from matplotlib.dates import DayLocator, DateFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.dates import DayLocator, DateFormatter

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'


# Read tide gauge data:
# ---------------------
csv_path = "../../../Data-for-teaching-staff/Floods/Harvey_flood_data/CO-OPS_8770777_wl_Harvey_Houston_TX.csv.gz"
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

# Drop the originals and set as index
df = df.drop(columns=["Date", "Time (GMT)"]).set_index("datetime").sort_index()

# Ensure numeric columns (coerce will turn any non-numeric leftovers into NaN)
for col in ["Predicted (m)", "Verified (m)"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

flood_thresholds = [0.628,0.872,1.024]

# Read precipitation data:
# ------------------------
fn = "../../../Data-for-teaching-staff/Floods/Harvey_flood_data/station_data_BAYTOWN_TX_4132729.csv.gz"
df1 = pd.read_csv(fn)

# build datetime from year/month/day
df1["date"] = pd.to_datetime(df1["DATE"])

# make sure precipitation is numeric; drop rows with missing values
df1["prcp"] = pd.to_numeric(df1["PRCP"], errors="coerce")
df1 = df1.dropna(subset=["prcp"]).sort_values("date")


# Prepare data for students:
# --------------------------
hurricane_Harvey_flood_data={"tide-gauge-time" : df.index,
                             "tide-gauge-predicted" : df["Predicted (m)"],
                             "tide-gauge-observed" : df["Verified (m)"],
                             "flood-thresholds" : flood_thresholds[:],
                             "precipitation-time" : df1["date"],
                             "precipitation-data" : df1["prcp"]
                             }



# Plot daily precipitation over time:
# -----------------------------------
fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8, 6))
x=hurricane_Harvey_flood_data["precipitation-time"]
y=hurricane_Harvey_flood_data["precipitation-data"]
ax[0].plot(x, y,linewidth=1.0)
start = pd.Timestamp("2000-01-01")
end   = pd.Timestamp("2024-12-31")
ax[0].set_xlim(start, end)
ax[0].set_title("Houston Daily Precipitation")
ax[0].set_xlabel("Year")
ax[0].set_ylabel("Precipitation (mm/day)")
ax[0].grid(True, alpha=0.3)


# Plot inset with August/September 2017 daily precipitation:
axins = inset_axes(
    ax[0],
    width="30%", height="45%",
    loc="upper left",                 # still anchored to the top-left
    bbox_to_anchor=(0.08, 0.0, 1, 1),# ← move right by 8% of the axes width
    bbox_transform=ax[0].transAxes,   # interpret bbox_to_anchor in axes coords
    borderpad=1.0
)

axins.bar(x, y, width=1.0, align="center")
axins.set_title("August/September 2017", fontsize=8, pad=2)
start = pd.Timestamp("2017-08-20")
end   = pd.Timestamp("2017-09-7")
axins.set_xlim(start, end)
axins.xaxis.set_major_locator(DayLocator(interval=5))
axins.xaxis.set_minor_locator(DayLocator(interval=1))
axins.xaxis.set_major_formatter(DateFormatter("%m/%d"))
for label in axins.get_xticklabels():
    label.set_rotation(0)
    label.set_fontsize(7)
for label in axins.get_yticklabels():
    label.set_fontsize(7)
axins.tick_params(length=2, pad=1)
#axins.set_ylabel("mm/day", fontsize=7)
axins.grid(True, alpha=0.3)



# Plot water level, predicted vs observed:
# ----------------------------------------
time = hurricane_Harvey_flood_data["tide-gauge-time"]
predicted = hurricane_Harvey_flood_data["tide-gauge-predicted"]
observed = hurricane_Harvey_flood_data["tide-gauge-observed"]
thresholds = hurricane_Harvey_flood_data["flood-thresholds"]
ax[1].plot(time, predicted, label="Predicted (m)", linewidth=1.0)
ax[1].plot(time, observed, label="Verified (m)", linewidth=1.0)

# add dash lines for floods thresholds: linestyle (offset, (on, off, on, off, ...))
ax[1].plot(time, predicted*0+thresholds[2], label="_nolegend_", linewidth=0.5, color='red',linestyle=(0, (14, 4)))
ax[1].plot(time, predicted*0+thresholds[1], label="_nolegend_", linewidth=0.5, color='black',linestyle=(0, (14, 4)))
ax[1].plot(time, predicted*0+thresholds[0], label="_nolegend_", linewidth=0.5, color='gray',linestyle=(0, (14, 4)))

ax[1].set_title("Water level, Hurricane Harvey, August 2017")
ax[1].xaxis.set_major_locator(DayLocator(interval=2))
ax[1].xaxis.set_major_formatter(DateFormatter("%m/%d"))
ax[1].xaxis.set_minor_locator(MultipleLocator(1.0))
ax[1].tick_params(axis='x', which='major', labelbottom=True)
ax[1].grid(which='both', alpha=0.3)
ax[1].set_xlabel("Date")
ax[1].set_ylabel("Water level (m)")


# adjust subplot locations:
fig.subplots_adjust(hspace=0.35)


# save to npy file to be pickeled for students later:
np.save("Output/to-pickle/hurricane_Harvey_flood_data.npy", hurricane_Harvey_flood_data)

