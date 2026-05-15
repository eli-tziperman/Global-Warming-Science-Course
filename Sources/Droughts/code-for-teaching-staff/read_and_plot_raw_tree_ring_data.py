# read bigcone Douglas-fir records from San Bernardino Mountains,
# convert to units of 0.01 mm, prepare for pickling for students.
# Eli

import numpy as np
import matplotlib.pyplot as plt
import os
import pickle

DEBUG=False

def read_tree_ring_widths_file(filename,years,data):
    linenum=0;
    idatapoint=0
    header_length=0 # set to 3 for input files with a 3-line header
    individual_tree_years=[]
    individual_tree_widths=[]
    with open(filename) as fp:
        if DEBUG:
            print("filename=",filename)
        for line in fp:
            linenum=linenum+1
            # skip header in first three lines:
            if linenum > header_length:
                # skipping first, which is tree sample identifier:
                numbers_on_line=[int(x) for x in line.split()[1:]]
                i=0 # counter for numbers appearing on a given line
                for x in numbers_on_line:
                    i=i+1
                    if i==1: # first number is the start year
                        start_year_on_this_line=x
                    # rest of numbers are tree ring widths, save them to data array:
                    if i>1 and x != 999 and x != -9999:
                        data.append(x)
                        # calculate the year for this width data:
                        iyear=start_year_on_this_line+i-2
                        years.append(iyear)
                        individual_tree_years.append(iyear)
                        individual_tree_widths.append(x)
                        # set threshold to something reasonable to see outliers:
                        if x > 60000:
                            print("large width found for: ",filename,iyear,x)
                    if x == 999: # units are 0.01 mm
                        all_individual_tree_records_years.append(individual_tree_years)
                        all_individual_tree_records_widths.append(individual_tree_widths)
                        if DEBUG:
                            print(individual_tree_years,individual_tree_widths)
                        individual_tree_years=[]
                        individual_tree_widths=[]
                    if x == -9999: # units are 0.001 mm, convert to 0.01 mm:
                        all_individual_tree_records_years.append(individual_tree_years)
                        all_individual_tree_records_widths.append(10*individual_tree_widths)
                        if DEBUG:
                            print(individual_tree_years,individual_tree_widths)
                        individual_tree_years=[]
                        individual_tree_widths=[]

    return years,data,all_individual_tree_records_years,all_individual_tree_records_widths

########################################################################
## Main program:
########################################################################

# Make a list of all data files:
file_list=[]
data_directory="../../../Data-for-teaching-staff/Droughts/NOAA-tree-ring-data/"
for i in os.listdir(data_directory):
    file_list.append(os.fsdecode(i))
file_list.sort()

# read all data files, accumulate individual tree records and their
# time axes in the lists all_individual_tree_records_years/widths, and
# accumulate all data points/ years in widths/years lists
years=[]
widths=[]
all_individual_tree_records_years=[]
all_individual_tree_records_widths=[]
for file in file_list:
    if file.endswith(".rwl"):
        filename=data_directory + file
        #filename='ca662_rwl.txt'
        years,widths,all_individual_tree_records_years,all_individual_tree_records_widths \
            =read_tree_ring_widths_file(filename,years,widths)

years=np.asarray(years)
widths=np.asarray(widths)

# ------------------------------------------------------------
# plot raw widths and bin-averaged widths as function of year:
# ------------------------------------------------------------

fig=plt.figure(1,figsize=(10,5))
# plot raw widths as a scatter plot:
# ----------------------------------
plt.plot(years,widths,".",markersize=0.5,label="raw data")
plt.xlabel("years")
plt.ylabel("ring width (0.01 mm)")
plt.title("San Bernardino Mountains, bigcone Douglas-fir")
# change to True to plot raw widths as individual time series:
if False:
    for i in range(0,len(all_individual_tree_records_widths)):
        plt.plot(all_individual_tree_records_years[i]\
                 ,all_individual_tree_records_widths[i]\
                 ,color="grey",linewidth=0.5)

# calculate and plot binned-average values:
# -----------------------------------------
year_start=np.floor(np.min(years)/10)*10
year_end=np.ceil(np.max(years)/10)*10
nbins = int(np.round((year_end-year_start)/10))
#print("start/end years: ",year_start,year_end)
n, edges = np.histogram(years, bins=nbins,range=(year_start,year_end))
widths_binned, _ = np.histogram(years, weights=widths \
                                ,bins=nbins,range=(year_start,year_end))
widths_binned=widths_binned/n
time_axis=np.nan*edges
for i in range(1,len(time_axis)):
    time_axis[i-1]=(edges[i]+edges[i-1])/2.0
plt.plot(time_axis[0:len(time_axis)-1]\
         ,widths_binned,'r-',linewidth=2,label="bin-average")

# calculate and plot mean of binned average values:
# -------------------------------------------------
mean_width=np.mean(widths_binned)
plt.plot(time_axis[0:len(time_axis)-1],0*widths_binned+mean_width \
         ,color='r',dashes=[12,6],linewidth=0.75,label="mean of bin-avg")
plt.legend()
plt.savefig("./Output/Figures/droughts-tree-ring-records-and-bin-average.pdf")


# ----------------------------
# plot distribution of widths:
# ----------------------------
fig=plt.figure(2,figsize=(6,5))
plt.xlabel("width")
plt.ylabel("# of occurences")
plt.title("histogram of widths")
nbins = 50
hist,edges=np.histogram(widths, bins=nbins)
time_axis=np.nan*edges
for i in range(1,len(time_axis)):
    time_axis[i-1]=(edges[i]+edges[i-1])/2.0
plt.plot(time_axis[0:len(time_axis)-1],hist,'.')
plt.savefig("./Output/Figures/droughts-tree-ring-distribution-of-widths.pdf")
plt.show()

# -----------------------
# save data for students:
# -----------------------
# np.save("Output/all_individual_tree_records_widths.npy", all_individual_tree_records_widths)
# np.save("Output/all_individual_tree_records_years.npy", all_individual_tree_records_years)

with open('Output/all_individual_tree_records.pickle', 'wb') as file:
    # Save the two variables in a dictionary or tuple
    pickle.dump({
        'all_individual_tree_records_years': all_individual_tree_records_years,
        'all_individual_tree_records_widths': all_individual_tree_records_widths
    }, file)
