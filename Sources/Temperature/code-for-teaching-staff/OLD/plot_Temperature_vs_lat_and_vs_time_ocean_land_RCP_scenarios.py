#__doc__
"""
This script plots comparisons of SAT in different RCP scenarios.
Specifically, it plots warming as a function of latitude and plots
temperature as a function of year for all combinations of 
{winter, summer} and {sea, land}, for RCP scenarios 3.6, 4.5, and 8.5

Files Required
    A landmask for GFDL-CM3 or compatible, in the format of a
    .nc file (used: https://data1.gfdl.noaa.gov/CM2.X/faq/question_19.html)

    .npy files containing monthly SAT maps for RCP 2.6, 4.5, and 8.5

To use, ensure that the variable RCP_LANDMASK_PATH found directly
below this __doc__ string contains a valid path to the landmask described
above, the variable RCP_LANDMASK_NAME contains the name of the variable
within the .nc file which contains the landmask data, and the three
RCP*_NPY variables contain the path to their respective .npy file as
described above.

Yonathan Vardi 2019-07-15
"""
########################################################################
# https://data1.gfdl.noaa.gov/CM2.X/faq/question_19.html
RCP_LANDMASK_PATH = "../../../Data-for-teaching-staff/Temperature/sftlf_A1.static.nc"
RCP_LANDMASK_NAME = "sftlf"
RCP26_NPY = "Output/rcp26/rcp26_monthly_SAT_map.npy"
RCP45_NPY = "Output/rcp45/rcp45_monthly_SAT_map.npy"
RCP85_NPY = "Output/rcp85/rcp85_monthly_SAT_map.npy"
########################################################################

import numpy as np
from math import radians

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib

#convert the mask to a usable format
def percent_land_mask_to_bool_land_mask(input_mask):
    land = input_mask >= 50
    land = np.ma.filled(land, False)
    return land


class Scenario:
    """
    This class represents either an RCP scenario or observed data.
    It calculates various maps and means, and allows them to be
    plotted.
    """
    def __init__(self, monthly_data, land_mask):
        """
        Params:
            monthly_data- a 3D numpy array time series of SAT maps given
                at a monthly interval.
            land_mask- a 2D numpy array of True or False values, where 
                True represents land and False represents water. Must
                have the same shape as monthly_data.
        """
        self.land_mask = land_mask
        self.sea_mask = np.bitwise_not(land_mask)
        self.summer_maps = self._get_summer_maps(monthly_data)
        self.winter_maps = self._get_winter_maps(monthly_data)
        self.summer_land = self._apply_mask(self.summer_maps, self.sea_mask)
        self.summer_sea = self._apply_mask(self.summer_maps, self.land_mask)
        self.winter_land = self._apply_mask(self.winter_maps, self.sea_mask)
        self.winter_sea = self._apply_mask(self.winter_maps, self.land_mask)

    #################################################################### private

    def _get_summer_maps(self, input_map):
        """Return maps of the average SAT of every year during summer

        Params:
            input_map- 3D numpy array of floats representing the
                monthly average SAT

        Return a 3D numpy array of floats time series of maps of the
            average summertime SAT
        """
        year_maps = []
        for i in range(1, len(input_map), 12):
            months = input_map[i+5:i+8]
            year_maps.append(np.mean(months, axis=0))
        return np.asarray(year_maps)

    def _get_winter_maps(self, input_map):
        """Return maps of the average SAT of every year during summer

        Params:
            input_map- 3D numpy array of floats representing the
                monthly average SAT

        Return a 3D numpy array of floats time series of maps of the
            average summertime SAT
        """
        year_maps = []
        for i in range(1, len(input_map), 12):
            months = input_map[i-1:i+2]
            year_maps.append(np.mean(months, axis=0))
        return np.asarray(year_maps)
    
    def _apply_mask(self, input_map, input_mask):
        """Apply a 2D mask to a 3D map

        Params:
            input_map- 3D numpy array of floats
            input_mask- a 2D numpy array of bools. Its shape must be
                equal to input_map's shape along axes 1 and 2 (but not 0)

        Return input_map with input_mask applied to each of its layers.
        """
        #stack the input mask
        stacked_mask = []
        for _ in range(len(input_map)):
            stacked_mask.append(input_mask)
        stacked_mask = np.asarray(stacked_mask)
        # print(stacked_mask.shape, input_map.shape)
        return np.ma.masked_array(input_map, stacked_mask)
    
    def _get_mean_of_map(self, input_map):
        """Return the mean SAT from a 2D given map, taking into account
        the Earth's curvature and the presence of land.
        
        Params:
            input_map- 2D numpy array of floats. This represents a global 
                map of SST values in a given year.
        
        Return a float representing the mean SAT value in the map
        """
        input_map
        denominator = 0
        numerator = 0
        lat_axis = np.linspace(-90, 90, 90)[45:] # *Eli:, was [45:] northern hemisphere
        for i in range(input_map.shape[0]):
            weight = np.cos(radians(lat_axis[i]))
            s = np.sum(input_map[i])
            if s > 0 or s < 0:
                numerator += s * weight
                denominator += input_map[i].count() * weight
        if denominator == 0:
            print("ERROR DIV BY 0", numerator, denominator, input_map.shape[0])
            return np.nan
        return numerator/denominator

    ##################################################################### public

    def gmean_timeseries(self, input_map):
        """
        Return a time series of the global mean temperature for a given
        time series (3D) of maps

        Params:
            input_map- 3D numpy array of floats. Represents the time
                series of maps.
        
        Return a 1D numpy array of floats representing the global mean
            temperature for every map in the time series
        """
        means = []
        for i in range(len(input_map)):
            means.append(self._get_mean_of_map(input_map[i]))
        return np.asarray(means)

    def latitude_means(self, input_map):
        """Return the mean surface air temperature across each latitude
        for a given map

        Params: 
            input_map- 2D numpy array of floats. This represents a global 
                map of SAT values in a given year.

        Return a 1D numpy array of floats
        """
        lats = np.ma.mean(input_map, axis=1)
        return lats
    
    def draw_lat_plots(self, ax, name="", start_year=2006):
        """Plot the warming since the beginning of the dataset against
        latitude.

        Params:
            ax- A matplotlib Axes. The subplot that the plots will be
                drawn on.
            name- str, optional. The name of the scenario (e.g "RCP 2.6").
                Used for labeling only. Defaults to "".
            start_year- int, optional. The year that the data begins.
                Used for labeling only. Defaults to 2006, which is
                the value for RCP scenarios
        """
        lat_axis = np.linspace(-90, 90, 90)[:] # *Eli: was [45:] northern hemisphere
        ax.plot(lat_axis, self.latitude_means(self.winter_sea[-1]
                 - self.winter_sea[0]), color="teal", label="Winter Sea Temp.")
        ax.plot(lat_axis, self.latitude_means(self.summer_sea[-1]
                 - self.summer_sea[0]), color="cyan", label="Summer Sea Temp.")
        ax.plot(lat_axis, self.latitude_means(self.winter_land[-1]
                 - self.winter_land[0]), color="tan", label="Winter Land Temp.")
        ax.plot(lat_axis, self.latitude_means(self.summer_land[-1]
                 - self.summer_land[0]), color="gold", label="Summer Land Temp.")
        ax.set_ylabel("Warming since "+str(start_year)+" (°C)")
        ax.set_ylim(-2, 33)
        ax.set_xlim(-90,90)
        ax.set_xticks(range(-90,120,30))
        ax.set_xlabel("Latitude")
        ax.set_title(name)
        
    def draw_mean_plots(self, ax, name, start_year=2006):
        """
        Draw 
        """
        years = np.arange(start_year, start_year+len(self.summer_sea))
        ax.plot(years, self.gmean_timeseries(self.winter_sea)-273.15, color="teal",
                label="Northern Winter Sea Temp.")
        ax.plot(years, self.gmean_timeseries(self.summer_sea)-273.15, color="cyan",
                label="Northern Summer Sea Temp.")
        ax.plot(years, self.gmean_timeseries(self.winter_land)-273.15, color="tan",
                label="Northern Winter Land Temp.")
        ax.plot(years, self.gmean_timeseries(self.summer_land)-273.15, color="gold",
                label="Northern Summer Land Temp.")
        ax.set_ylim(1, 28)
        ax.set_xlabel("Year")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title(name)


########################################################################
## Main program:
########################################################################
        
# #load the prepared land mask for observed data
#load from file the land mask for projected data
rcp_land_mask = Dataset(RCP_LANDMASK_PATH, 'r').variables[RCP_LANDMASK_NAME][:]
rcp_land_mask = percent_land_mask_to_bool_land_mask(rcp_land_mask)

plt.ioff()
rcp45_npy = np.load(RCP45_NPY)
rcp45_npy = rcp45_npy[:-2400, :, :] #cut it so it's only 100 years
rcp26_npy = np.load(RCP26_NPY)
rcp85_npy = np.load(RCP85_NPY)

rcp26 = Scenario(rcp26_npy, rcp_land_mask)
rcp45 = Scenario(rcp45_npy, rcp_land_mask)
rcp85 = Scenario(rcp85_npy, rcp_land_mask)

fig,(ax1, ax2, ax3) = plt.subplots(1, 3,figsize=(12, 5))
rcp26.draw_lat_plots(ax1, "RCP2.6")
rcp45.draw_lat_plots(ax2, "RCP4.5")
rcp85.draw_lat_plots(ax3, "RCP8.5")
ax1.legend(loc="upper left")
plt.tight_layout()
plt.savefig("Output/Figures/temperature-RCP_temperature_vs_latitude.pdf",format='pdf');

#cut all npy files to northern hemisphere only
rcp26_npy = rcp26_npy[:, 45:, :]
rcp45_npy = rcp45_npy[:, 45:, :]
rcp85_npy = rcp85_npy[:, 45:, :]
rcp_land_mask = rcp_land_mask[45:]

rcp26 = Scenario(rcp26_npy, rcp_land_mask)
rcp45 = Scenario(rcp45_npy, rcp_land_mask)
rcp85 = Scenario(rcp85_npy, rcp_land_mask)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3,figsize=(12, 5))
rcp26.draw_mean_plots(ax1, "RCP2.6")
rcp45.draw_mean_plots(ax2, "RCP4.5")
rcp85.draw_mean_plots(ax3, "RCP8.5")
ax1.legend(loc="upper left")
plt.tight_layout()
plt.savefig("Output/Figures/temperature-RCP_temperature_timeseries.pdf",format='pdf');

plt.draw()
