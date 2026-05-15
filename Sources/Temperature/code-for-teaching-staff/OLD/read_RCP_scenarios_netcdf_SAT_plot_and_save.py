# -*- coding: utf-8 -*-
#__doc__
"""
This script extracts SAT data from multiple netCDF files.

Usage Instructions:
	This script requires several directories of
	netCDF files containing surface air temperature data:
	 - Files from an RCP8.5 simulation
	   (used: GFDL-CM3 RCP85 r1i1p1)
	 - Files from an RCP4.5 simulation
	   (used: GFDL-CM3 RCP45 r1i1p1)
	 - Files from an RCP2.6 simulation
	   (used: GFDL-CM3 RCP26 r1i1p1)
	 - Files from a historical simulation
	   (used: GFDL-CM3 historical r1i1p1)
	It also requires the GISTEMP dataset as a netCDF file
	(labeled "Land-Ocean Temperature Index,
	ERSSTv5, 1200km smoothing" on
	https://data.giss.nasa.gov/gistemp/)

    To use, ensure that the constants directly below this __doc__ string
    contain the correct paths and variable names, then run. The script
    will create the files specified in the Files Created section of this
    __doc__ string, and output a large number of plots to allow 
    verification that the data is correct. The script will not terminate
    until all plot windows have been closed.

Files Created:
    timemean.npy (1951-1980_timemean.npy):
        Map of the time mean of every lat/lon coordinate point between 1951-1980
        2D array of floats
        data is accessed via [lat, lon]
	[RCP26, RCP45, RCP85]/sat_global.npy:
        The absolute yearly average surface air temperature, in K
        Time series stored in a 2-row 2D array.
        array[0] = array of years
        array[1] = array of values
        Time series stored in a 2-row 2D array.
        array[0] = array of years
        array[1] = array of values
	[RCP26, RCP45, RCP85, OBS]/lat_average_timeseries.npy
        A time series of average temperature per latitude.
        in OBS, it is observed average temperature anomaly.
        2D array
        data accessed via [time, latitude]
	[RCP26, RCP45, RCP85, OBS]/lat_average_1st_year.npy
        The average temperature per latitude for the first
        year of data. For RCP scenarios this is 2006, for
        OBS this is 1880. Subtract this from
        lat_average_timeseries.npy to get total warming.
        1D array arranged by latitude

Yonathan Vardi 2019-07-12
"""
########################################################################
# Constants
########################################################################
# The paths to the directories containing the .nc RCP files
RCP26_PATH = "../../../Data-for-teaching-staff/Temperature/RCP26/"
RCP45_PATH = "../../../Data-for-teaching-staff/Temperature/RCP45/"
RCP85_PATH = "../../../Data-for-teaching-staff/Temperature/RCP85/"
HISTORICAL_PATH = "../../../Data-for-teaching-staff/Temperature/historical/"
# The name of the variable within the .nc file containing SAT data
# (variable names assumed to be uniform between all RCP files)
RCP_DATA_NAME = "tas" 
# The name that the latitude and longtitude axis variables are given
RCP_LAT_NAME = "lat"
RCP_LON_NAME = "lon"
# The year for which the data begins
RCP_START = 2006
# The path to the .nc *FILE* (NOT directory) containing the OBS(erved) data
OBS_PATH = "../../../Data-for-teaching-staff/Temperature/gistemp1200_GHCNv4_ERSSTv5.nc"
# The name of the variable within the .nc file containing SAT data
OBS_DATA_NAME = "tempanomaly"
# The name that the latitude and longtitude axis variables are given
OBS_LAT_NAME = "lat"
OBS_LON_NAME = "lon"
# The year for which the data begins
OBS_START = 1880
########################################################################
########################################################################

import numpy as np
import numpy.ma as ma
from math import radians
import os

import matplotlib.pyplot as plt
import matplotlib as mpl
from netCDF4 import Dataset

########################################################################
# read_analyze_plot_SAT        
########################################################################

class read_analyze_plot_SAT:
    """
    The read_analyze_plot_SAT class.
    This class extracts data from a netCDF file containing SAT data in
    the form of a map (see __doc__ at top of file for exact specifications)
    It can also do some basic plotting.

    ###############################################################
    # IMPORTANT: either read_analyze_plot_SAT.initialize() or 
    # read_analyze_plot_SAT.initialize_SAT_from_RCP() MUST be called to initialize
    # this class
    ###############################################################

    Public Members:
        map - 3D numpy array of floats. This is taken directly from the
            provided netCDF file, and represents the raw SAT data. The
            first dimension is time, the second dimension is latitude, and the 
            third dimension is longtitude.
            
        lat_axis - 1D numpy array of ints. This is taken directly from the
            provided netCDF file, and represents the latitudes that self.map
            corresponds to.

        lon_axis - 1D numpy array of ints. This is taken directly from the
            provided netCDF file, and represents the longtitudes that self.map
            corresponds to.

        time_mean - 2D numpy array of floats. This is a map representing the
            time mean of the data in self.map (The mean value of each 
            latitude-longtitude point across the time axis). The first 
            dimension is latitude, and the second dimension is longtitude.

        yearly_map - 3D numpy array of floats. This is similar to self.map, 
            except that each plane along the time axis represents the time-mean
            SAT of a given year. The first dimension is time, the second 
            dimension is latitude, and the third dimension is longtitude.

        smooth_map - 3D numpy array of floats. This is similar to yearly_map,
            except that it has undergone smoothing.
            
    Public Methods:
        *More detailed descriptions in docs of individual methods
        
        get_year_anomaly_map()->2D array - Return a map showing the 
            anomaly between a given year and the time-mean SAT in the form of 
            a 2D numpy array of floats.
            
        get_year_anomaly_map_smooth()->2D array - Return a map showing
            the anomaly between the time-mean and a given year after it has
            undergone smoothing. Return value is a 2D numpy array of floats.
            
        contour_anomaly_progression() - Save a series of images showing the
            progression of the anomaly maps throughout the years. Useful for
            animating.
            
        plot_SAT_averages() - Plot the unsmoothed mean SAT value and the 
            smoothed mean SAT value for a given range of years, as well as the 
            overall time-mean of the entire dataset.

        save_GMST_data() - Save the global average SAT values as
            2 .npy files. See __doc__ at top of script for more.
    
    """

    ###########################################################################
    # INITIALIZERS    
    # important: either read_analyze_plot_SAT.initialize() or 
    # read_analyze_plot_SAT.initialize_SAT_from_RCP() MUST be called to initialize
    # this class
    ###########################################################################

    def __init__(self):
        # this is a flag for whether one of the constructor functions has
        # been manually called. No functions will work until this flag
        # is set to True.
        self._initialized = False
    
    def initialize(self, filepath, data_name, lat_name, lon_name, start_year, 
              smooth=5, dpy=12, mean=None):
        """
        Construct an instance of the read_analyze_plot_SAT class given a single
        netCDF file. For datasets composed of multiple files, use
        read_analyze_plot_SAT.initialize_SAT_from_RCP()
        
        Params:
            filepath- str. A filepath to a netCDF file containing SAT data in
                the form of a map. More information regarding specifications
                of the data in the file can be found in __doc__ at top of file.
                (e.g "../../../Data-for-teaching-staff/Temperature/sat.nc")
            data_name- str. The name of the variable within the netCDF file
                containing the SAT data. (e.g "sat")
            lat_name- str. The name of the variable within the netCDF file
                containing the latitudes of each map row.
            lon_name- str. The name of the variable within the netCDF file
                containing the longtitudes of each map column.
            start_year- int. The first year for which the netCDF file contains
                SAT data. This is used for labeling purposes.
            
        Optional Params:    
            smooth- odd int. The amount of years over which smooth data should 
                be smoothed. For example, if the value 3 is given, all the 
                smooth data will undergo 3-year-smoothing. The higher the
                number, the smoother that data will be. This does not affect
                cases where unsmoothed data is used. Defaults to 5.
            dpy- int. Divisions per year. The number of maps per year of data
                in the netCDF file. For example, if the netCDF file contains
                monthly SAT maps, this value should be 12; if it contains yearly
                SAT maps, it should be 1. Defaults to 12.
            mean- 2D numpy array of floats. This represents a map of the
                time-mean for any period. If this is none, a map of means 
                is computed based on the netCDF data provided, but if an array
                is given that array is used as the time-mean. This allows
                multiple data sets to be compared as anomalies of the same mean.
                Defaults to None.
        """
        #load values from netCDF
        ncfile = Dataset(filepath, 'r')
        self.map = ncfile.variables[data_name][:]
        self.lat_axis = ncfile.variables[lat_name][:]
        self.lon_axis = ncfile.variables[lon_name][:]
        self._generic_constructor(start_year, smooth, dpy, mean)
        print("successfully initialized from file")

    def initialize_SAT_from_RCP(self, directory, data_name, lat_name, lon_name, start_year, 
              smooth=5, dpy=12, mean=None):
        """
        Construct an instance of the read_analyze_plot_SAT class given a directory
        containing netCDF file.
        
        For datasets composed of one file, use read_analyze_plot_SAT.initialize()
        
        Params:
            directory- str. The directory containing the netCDF files
                (final "/" included). All .nc files found in this 
                directory will be opened, and files are assumed to contain 
                data ordered chronologically by their name. That is, file 
                "b.nc" is assumed to be a direct continuation of the data 
                in "a.nc". Files are also assumed to have identically named 
                variables.
                (e.g "../../../Data-for-teaching-staff/Temperature/")

            for documentation regarding the other parameters, see 
            read_analyze_plot_SAT.initialize()
        """
        #begin by making a list of all .nc files
        file_list=[]
        for i in os.listdir(directory):
            file_list.append(os.fsdecode(i))
        file_list.sort()

        filenames = []
        for file in file_list:
            if file.endswith(".nc"):
                filenames.append(directory + file)

        #ensure there were files in directory
        if len(filenames) == 0:
            print("No .nc files in directory! Initialization failed!")
            return

        #then get the values from the first file (this is the only file
        # from which lat_axis and lon_axis are gotten)
        ncfile = Dataset(filenames[0], 'r')
        self.lat_axis = ncfile.variables[lat_name][:]
        self.lon_axis = ncfile.variables[lon_name][:]
        self.map = ncfile.variables[data_name][:]

        #then add the data from the rest of the files
        for i in range(1, len(filenames)):
            ncfile = Dataset(filenames[i], 'r')
            print("concatenating " + filenames[i])
            self.map = np.ma.concatenate((self.map,
                          ncfile.variables[data_name][:]))

        self._generic_constructor(start_year, smooth, dpy, mean)
        print("successfully initialized from directory")

    def _generic_constructor(self, start_year, smooth, dpy, mean):
        """A function called by all constructors that does all the
        construction which is independant from the data's source
        """
        #mark this instance of read_analyze_plot_SAT as being initialized
        self._initialized = True

        #if longtitudes start at negative values, convert it to a 0-360 format
        #(this was added for a specific case)
        if self.lon_axis[0] < 0:
            self.lon_axis -= self.lon_axis[0]
        # if self.lat_axis[0] < 0:
        #     self.lat_axis = np.flip(self.lat_axis)

        #set the smoothness factor
        self._smooth = smooth
        #calculate the time-mean map once and store it, or use the given value
        self.time_mean = None
        if mean is None:
            self.time_mean = self._get_timemean_SAT_map()
        else:
            self.time_mean = mean
        #calculate the maps of yearly averages
        self.yearly_map = self._get_yearly_average_maps(dpy)
        self.smooth_map = self._get_yearly_average_maps_smooth(self.yearly_map)
        
        self.start_year = start_year
        
        #calculate the 1D data used for plotting and store it
        # this is the overall average global temperature of the entire dataset. 
        # It is a float
        self._global_time_mean = self._get_mean_of_map(self.time_mean)
        # these are the smoothed and unsmoothed global mean SAT anomalies as they
        # progress through time.
        # both are 1D numpy arrays of floats
        self._smoothed_mean = []
        self._unsmoothed_mean = []
        for i in range(len(self.yearly_map)):
            self._unsmoothed_mean.append(
                    self._get_mean_of_map(self.get_year_anomaly_map(i)))
            self._get_mean_of_map(self.yearly_map[i])
        for i in range(len(self.smooth_map)):
            self._smoothed_mean.append(
                self._get_mean_of_map(self.get_year_anomaly_map_smooth(i)))
        self._smoothed_mean = np.asarray(self._smoothed_mean)
        self._unsmoothed_mean = np.asarray(self._unsmoothed_mean)

        
    ############################################################ private methods
        
    def _get_timemean_SAT_map(self):
        """Return a map of the time-mean SAT
        
        Return a 2D numpy array of floats representing the time-mean of every
        longtitude and latitude
        """
        time_mean = np.mean(self.map, axis=0)
        return time_mean
    
    def _get_yearly_average_maps(self, divisions_per_year=12):
        """Return maps of the average SAT of every year
        
        Params:
            divisions_per_year - int, optional. See documentation of 'dpy' in
                __init__()
        
        Return a 3D numpy array of floats. The first axis represents time, with
        a 1-year interval. At each point along this axis is a 2D numpy array
        of floats representing the yearly average of every longtitude and 
        latitude for a single year
        """
        year_maps = []
        for i in range(0, len(self.map), divisions_per_year):
            months = self.map[i:i+divisions_per_year]
            year_maps.append(np.mean(months, axis=0))
        return np.asarray(year_maps)
    
    def _get_yearly_average_maps_smooth(self, averages):
        """Return a smoothed version of the yearly average maps
        
        Return a 3D numpy array of floats representing the smoothed map. Format
        is identical to _get_yearly_average_maps()
        """
        av = averages
        for _ in range(self._smooth//2):
            # the new values are stored here to prevent bias based on 
            # order in the list
            temp_av = []
            for j in range(1, len(av)-1):
                temp_av.append(.5*av[j]+.25*(av[j-1]+av[j+1]))
            # replace the old PDI list with the new one
            av = temp_av
        return np.asarray(av)

    def _get_mean_of_map(self, input_map):
        """Return the mean SAT from a given map, taking into account
        the Earth's curvature and the presence of land.
        
        Params:
            input_map- 2D numpy array of floats. This represents a global 
                map of SAT values in a given year.
        
        Return a float representing the mean SAT value in the map
        """
        denominator = 0
        numerator = 0
        for i in range(input_map.shape[0]):
            weight = np.cos(radians(self.lat_axis[i]))
            s = np.sum(input_map[i])
            if s > 0 or s < 0:
                numerator += s * weight
                denominator += np.count_nonzero(input_map[i]) * weight
        return numerator/denominator

    ############################################################# public methods

    def get_regional_av_of_2D_map(self, input_map):
        """Return the mean surface air temperature across each latitude
        for a given map

        Params: 
            input_map- 2D numpy array of floats. This represents a global 
                map of SAT values in a given year.

        Return a 1D numpy array of floats
        """
        lats = np.mean(input_map, axis=1)
        # print(input_map.shape, len(lats))
        return lats

    def get_time_series_reg_avs_of_3D_map(self, input_map):
        """Return a time series of regional (latitude) averages for a
        time series of 2D maps

        Params: 
            input_map- 3D numpy array of floats. This represents a time series 
                of 2D maps of SAT values.

        Return a 2D numpy array of floats. The first axis is time, and the
            second axis is latitude
        """
        time_series = []
        #loop through every point in time
        for i in input_map:
            #append its regional averages to the time series
            time_series.append(self.get_regional_av_of_2D_map(i))
        #turn time series into array and return it
        return np.asarray(time_series)
    
    def get_year_anomaly_map(self, year):
        """Return a map of the anomaly between the SAT of every point on map
        during the given year and its time-mean SAT.
        
        Param:
            year- int. The year since the first year in the dataset whose
                anomaly to return
        
        Return a 2D numpy array of floats representing a map of the anomaly
        """
        if not self._initialized:
            print("Class not initialized! Initialize class by calling",
                  "initialize() or initialize_SAT_from_RCP()!")
        return self.yearly_map[year] - self.time_mean
    
    def get_year_anomaly_map_smooth(self, year):
        """Return a map of the anomaly between the SAT of every point on map
        during the given year, with smoothing applied, and its time-mean 
        SAT.
        
        Param:
            year- int. The year whose anomaly to return. This year should be
                 at least two years away from the edge of the unsmoothed dataset.
        
        Return a 2D numpy array of floats representing a map of the anomaly.
        """
        if not self._initialized:
            print("Class not initialized! Initialize class by calling",
                  "initialize() or initialize_SAT_from_RCP()!")
        return self.smooth_map[year] - self.time_mean
    
    def contour_anomaly_progression(self, title, path):
        if not self._initialized:
            print("Class not initialized! Initialize class by calling",
                  "initialize() or initialize_SAT_from_RCP()!")
            return
        #set up plot
        self.figure, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 10))

        anomaly = self.get_year_anomaly_map_smooth(len(self.smooth_map)-1)
        cmap = mpl.cm.coolwarm
        norm = mpl.colors.Normalize(vmin=-2, vmax=2)
        cb_setter_array = np.asarray([np.arange(-3,3,.01), np.arange(-3,3,.01)])
        cb_setter = self.ax1.contourf(cb_setter_array, 99, norm=norm, cmap=cmap)
        clb = self.figure.colorbar(cb_setter, ax=self.ax1)
        clb.set_label('Anomaly (°C)')
        for i in range(0, len(self.smooth_map)):
            print("Saved map of", i+self.start_year+(self._smooth//2), end="\r")
            anomaly = self.get_year_anomaly_map_smooth(i)
            #automatically mention in title whether smoothing is applied or not
            smooth_str = ""
            if self._smooth > 1:
                smooth_str = " (" + str(self._smooth) + "-year-smoothed)"
            self.ax1.clear()
            self.ax1.set_title(title + smooth_str + "\n" + 
                        str(self.start_year + (self._smooth//2) + i))
            self.ax1.contourf(self.lon_axis, self.lat_axis, 
                        anomaly, 100, norm=norm, cmap=cmap)
            self.plot_SAT_averages(self.start_year+(self._smooth//2)+i)
            self.ax1.get_xaxis().set_ticks([])
            self.ax1.get_yaxis().set_ticks([])
            self.figure.draw()
            plt.savefig(path + "/map-" + str(i).rjust(5, '0') + ".png")
                
    def plot_SAT_averages(self, end_year):
        """Plot the average SAT values up to the given year"""
        if not self._initialized:
            print("Class not initialized! Initialize class by calling",
                  "initialize() or initialize_SAT_from_RCP()!")
            return
        unsmoothed_mean = self._unsmoothed_mean[
                self._smooth//2:end_year-self.start_year]
        smoothed_mean = self._smoothed_mean[:
            end_year-self.start_year-(self._smooth//2)]
        year_range = range(self.start_year + (self._smooth//2), end_year)
        self.ax2.clear()
        self.ax2.set_title("Global SAT")
        self.ax2.set_xlabel("Year")
        self.ax2.set_ylabel("Anomaly (°C)")
        self.ax2.hlines(y=0, xmin=self.start_year+(self._smooth//2),
                        xmax=end_year+(self._smooth//2)
                                , label="time mean")
        self.ax2.plot(year_range, unsmoothed_mean, label="Average SAT")
        self.ax2.plot(year_range, smoothed_mean, label="Average SAT ("
                      + str(self._smooth) + "-year-smoothed)")
        self.ax2.legend(loc='upper left')
        
    def save_GMST_data(self, directory=""):
        """
        Save the yearly global average SAT and smoothed yearly global 
        average SAT for the entire record with the correct year range. 
        More information regarding format found in section 'Output' of __doc__ 
        at top of file.

        Params:
            directory- str. The directory within ./Output/ in which to place
                the saved files. Include final "/" but not initial one
                ("mydir/" is good; "mydir" and "/mydir" are not) Defaults to ""
        """
        if not self._initialized:
            print("Class not initialized! Initialize class by calling",
                  "initialize() or initialize_SAT_from_RCP()!")
            return

        #get the arrays of data
        unsmoothed_mean = []
        smoothed_mean = []
        for i in range(len(self.yearly_map)):
            unsmoothed_mean.append(self._get_mean_of_map(self.yearly_map[i]))
        for i in range(len(self.smooth_map)):
            smoothed_mean.append(self._get_mean_of_map(self.smooth_map[i]))
        unsmoothed_mean = np.asarray(unsmoothed_mean)
        smoothed_mean = np.asarray(smoothed_mean)
            
        #get the array of years it corrosponds to
        unsmoothed_mean_range = range(self.start_year, 
                    self.start_year + len(self.yearly_map))
        #bundle the two together
        raw = np.asarray([unsmoothed_mean_range, unsmoothed_mean])
        
        #repeat the process for the smoothed SAT data
        smoothed_mean_range = range(self.start_year + (self._smooth//2), 
                    self.start_year + len(self.smooth_map) 
                                + (self._smooth//2))
        smooth = np.asarray([smoothed_mean_range, smoothed_mean])

        #create output directory and save output:
        try:
            os.mkdir("Output/"+directory[-6:-1])
        except OSError:
            print ("failed to create directory %s, may have already existed" % "Output/"+directory[-6:-1] )
        else:
            print ("created directory %s " % "Output/"+directory[-6:-1])
        
        np.save("Output/"+directory+directory[-6:-1]+"_GMST_annual_anomaly_timeseries.npy", raw)
    
    def save_timemean_map(self, directory="", slice_tuple=None):
        """
        Save the map of the time mean to file. This allows it to be used
        to compare with other data sets.

        Params:
            directory- str. The directory within ./Output/ in which to place
		        the saved files. Include final "/" but not initial one
                ("mydir/" is good; "mydir" and "/mydir" are not) Defaults to ""
            slice_tuple- (int, int). If given a value, this will recalculate 
                the time-mean to only apply within the given years (including 
                first year but excluding last). Defaults to None.
        """
        to_save = self.time_mean
        if slice_tuple != None:
            to_save = np.mean(self.map[slice_tuple[0]:slice_tuple[1], :, :], 
                              axis=0)
        to_save = np.ma.filled(to_save, np.nan)
        np.save("Output/"+directory+"timemean-map-1951-1980.npy", to_save)

    def save_latitude_mean_timeseries(self, directory=""):
        """
        Save to file a time series of mean SAT per latitude, and
        save to file the mean SAT per latitude for the first year.

        Params:
            directory- str. The directory within ./Output/ in which to place
		        the saved files. Include final "/" but not initial one
                ("mydir/" is good; "mydir" and "/mydir" are not) Defaults to ""
        """
        time_series = self.get_time_series_reg_avs_of_3D_map(self.yearly_map)
        first_year = self.get_regional_av_of_2D_map(self.yearly_map[0])
        try:
            os.mkdir("Output/"+directory)
        except OSError:
            print ("failed to create directory %s" % "Output/"+directory[-6:-1])
        else:
            print ("created directory %s " % "Output/"+directory[-6:-1])

        np.save("Output/"+directory+directory[-6:-1]+"_lat_average_timeseries.npy", time_series)
        np.save("Output/"+directory+directory[-6:-1]+"_lat_average_1st_year.npy", first_year)

    def save_monthly_and_5yr_maps_and_axes(self, directory=""):
        # save monthly maps:
        monthly_map = np.ma.filled(self.map, np.nan)
        #np.save("Output/"+directory+directory[-6:-1]+"_monthly_SAT_map.npy", monthly_map)
        axes = np.empty(2, dtype=object)
        axes[0] = np.asarray(self.lat_axis)
        axes[1] = np.asarray(self.lon_axis)
        # axes = np.asarray([self.lat_axis, self.lon_axis])
        np.save("Output/"+directory+directory[-6:-1]+"_SAT_map_lat.npy", axes[0])
        np.save("Output/"+directory+directory[-6:-1]+"_SAT_map_lon.npy", axes[1])
        # Eli:
        # calculate and save 5 year means at start and end of run:
        first_5yr_map=np.mean(monthly_map[0:60,:,:],axis=0)
        last_5yr_map=np.mean(monthly_map[-60:,:,:],axis=0)
        np.save("Output/"+directory+directory[-6:-1]+"_SAT_map_first_5yr.npy", first_5yr_map)
        np.save("Output/"+directory+directory[-6:-1]+"_SAT_map_last_5yr.npy", last_5yr_map)


########################################################################
# End of defining class read_analyze_plot_SAT 
########################################################################


########################################################################
# Main program:
########################################################################

historical = read_analyze_plot_SAT()
historical.initialize_SAT_from_RCP(HISTORICAL_PATH, "tas", "lat", "lon", 1860)
historical.save_timemean_map(slice_tuple=(91, 121))

# load the 1951-1980 average and create an instance of the class for every
# scenario
mean = np.load("Output/timemean-map-1951-1980.npy")
RCP26 = read_analyze_plot_SAT()
RCP45 = read_analyze_plot_SAT()
RCP85 = read_analyze_plot_SAT()
obs = read_analyze_plot_SAT()
RCP26.initialize_SAT_from_RCP(RCP26_PATH, RCP_DATA_NAME, RCP_LAT_NAME, 
                              RCP_LON_NAME, RCP_START, mean=mean)
RCP45.initialize_SAT_from_RCP(RCP45_PATH, RCP_DATA_NAME, RCP_LAT_NAME, 
                              RCP_LON_NAME, RCP_START, mean=mean)
RCP85.initialize_SAT_from_RCP(RCP85_PATH, RCP_DATA_NAME, RCP_LAT_NAME, 
                              RCP_LON_NAME, RCP_START, mean=mean)
obs.initialize(OBS_PATH, OBS_DATA_NAME, OBS_LAT_NAME, OBS_LON_NAME, OBS_START)
RCP26.save_GMST_data("RCP26/")
RCP45.save_GMST_data("RCP45/")
RCP85.save_GMST_data("RCP85/")
RCP26.save_monthly_and_5yr_maps_and_axes("RCP26/")
RCP45.save_monthly_and_5yr_maps_and_axes("RCP45/")
RCP85.save_monthly_and_5yr_maps_and_axes("RCP85/")
RCP26.save_latitude_mean_timeseries("RCP26/")
RCP45.save_latitude_mean_timeseries("RCP45/")
RCP85.save_latitude_mean_timeseries("RCP85/")
obs.save_latitude_mean_timeseries("OBS/")

# RCP26.contour_anomaly_progression("RCP2.6 Surface Air Temperature", "./Output/RCP26/")

# plot time series of SAT from obs and RCP:
#plt.ioff()
fig, ax = plt.subplots()
ax.set_title("Global Average Annual SAT: RCP2.6")
ax.set_xlabel("Year")
ax.set_ylabel("Temperature (°C)")
x = np.load("./Output/RCP26/RCP26_GMST_annual_anomaly_timeseries.npy")
ax.plot(x[0], x[1]-273.15)
plt.savefig("Output/Figures/temperature-Global_Average_Annual_SAT_RCP26.pdf",format='pdf');

fig, ax = plt.subplots()
ax.set_title("Global Average Annual SAT: RCP4.5")
ax.set_xlabel("Year")
ax.set_ylabel("Temperature (°C)")
x = np.load("./Output/RCP45/RCP45_GMST_annual_anomaly_timeseries.npy")
ax.plot(x[0], x[1]-273.15)
plt.savefig("Output/Figures/temperature-Global_Average_Annual_SAT_RCP45.pdf",format='pdf');

fig, ax = plt.subplots()
ax.set_title("Global Average Annual SAT: RCP8.5")
ax.set_xlabel("Year")
ax.set_ylabel("Temperature (°C)")
x = np.load("./Output/RCP85/RCP85_GMST_annual_anomaly_timeseries.npy")
ax.plot(x[0], x[1]-273.15)
plt.savefig("Output/Figures/temperature-Global_Average_Annual_SAT_RCP85.pdf",format='pdf');

#plot warming by latitude
fig, ax = plt.subplots()
final_temp_26 = RCP26.get_regional_av_of_2D_map(RCP26.smooth_map[-1])
final_temp_45 = RCP45.get_regional_av_of_2D_map(RCP45.smooth_map[-200])
final_temp_85 = RCP85.get_regional_av_of_2D_map(RCP85.smooth_map[-1])
final_temp_obs = obs.get_regional_av_of_2D_map(obs.smooth_map[-1])
initial_temp = historical.get_regional_av_of_2D_map(historical.smooth_map[20])
initial_temp_obs = obs.get_regional_av_of_2D_map(obs.smooth_map[0])
d_temp_26 = final_temp_26 - initial_temp
d_temp_45 = final_temp_45 - initial_temp
d_temp_85 = final_temp_85 - initial_temp
d_temp_obs = final_temp_obs - initial_temp_obs
ax.plot(np.linspace(-90, 90, num=90), d_temp_26, label="RCP2.6, 2100")
ax.plot(np.linspace(-90, 90, num=90), d_temp_45, label="RCP4.5, 2100")
ax.plot(np.linspace(-90, 90, num=90), d_temp_85, label="RCP8.5, 2100")
ax.plot(np.linspace(-90, 90, num=90), d_temp_obs, label="Observed, 2019")
ax.set_xlabel("Latitude (°N)")
ax.set_ylabel("Temperature anomaly (°C)")
ax.set_title("Temperature Anomaly from 1880 by Latitude")
ax.legend(loc="upper left")
plt.savefig("Output/Figures/temperature-Observed_Temperature_Anomaly_lines_from_1880_by_Latitude.pdf",format='pdf');

plt.draw()
