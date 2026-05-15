# write a python code to read a space-separated text file "ghcnd-inventory.txt.gz" with 6 columns, and print out the lines where column 5 is larger than 1900 and column 6 is equal to 2023; interpret columns 1 and 2 as latitude and longitude and plot the locations corresponding to the printed lines on a global map using matplotlib. superimpose global coastlines

import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Define the file path
file_path = "~/Courses/EPS101/Data-for-teaching-staff/Floods/precipitation-station-data/ghcnd-inventory.txt.gz"

# Read the space-separated file into a pandas DataFrame
df = pd.read_csv(file_path, sep="\s+", header=None)

# Filter the DataFrame based on conditions
first = 1880
last = 2023
filtered_df = df[(df[4] <= first) & (df[5] == last) & (df[3]=="PRCP")]
print("full data shape=", df.shape, "filtered data shape=", filtered_df.shape)
number = filtered_df.shape[0]

# print long-duration stations:
filtered_df.to_csv("Output/long-duration-stations.csv", sep=',', index=False, encoding='utf-8')


# Plot locations on the map using matplotlib
fig, ax = plt.subplots(figsize=(10, 6),
                       subplot_kw={"projection": ccrs.PlateCarree()})
ax.scatter(
    filtered_df[2], filtered_df[1], marker="x",
    linewidth=0.25, s=12,
    color="red", label="Filtered Locations"
)
# Add coastlines and country boundaries
ax.coastlines(linewidth=0.2,color="blue",resolution='10m')
ax.add_feature(cfeature.BORDERS,linestyle='-',linewidth=0.2,color="gray")
plt.title(
    "Locations of %d long-duration stations from %d to %d"
    % (number, first, last)
)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.xlim(-180, 180)
plt.xticks(range(-150, 180, 30))
plt.yticks(range(-60, 90, 30))
plt.ylim(-90, 90)
plt.grid()

## save as pdf:
f = plt.gcf()  # f = figure(n) if you know the figure number
f.set_size_inches(8, 4)
f.savefig("Output/long-duration-stations-on-a-map.pdf",format='pdf');

plt.show()
