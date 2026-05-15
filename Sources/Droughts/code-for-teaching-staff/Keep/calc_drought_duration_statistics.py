# this code can be added as another cell in the workshop for students

## Optional: calculate drough duration statistics.
def calc_drought_durations(years,timeseries,pdsi_threshold):
    durations_list=[] # durations of all droughts beyond threshold
    last_drought_years_list=[] # last year of each drought event
    length_drought=1
    for i in range(1,len(timeseries)):
        if timeseries[i]<=pdsi_threshold and timeseries[i-1]<=pdsi_threshold:
            length_drought=length_drought+1
        elif timeseries[i-1]<=pdsi_threshold:
            durations_list.append(length_drought)
            last_drought_years_list.append(years[i])
            length_drought=1
            
    return durations_list,last_drought_years_list

# load data, separate it to time axis and pdsi time series:
pdsi_threshold=-3 # a drought is defined as being less than this value
pdsi=PDSI_timeseries
years=1.0*pdsi[0,:]
pdsi=1.0*pdsi[1,:]


# calculate drought durations:
durations_list,last_drought_years_list \
    =calc_drought_durations(years,pdsi,pdsi_threshold)
print("end year, drought duration:")
for i in range(0,len(durations_list)):
    print("%d,%d;" %(int(last_drought_years_list[i]),int(durations_list[i])),end=' ')
print(" ")

plt.rcParams['figure.dpi']= 300 # incrase default image resolution

# plot the distribution of drought periods (how many droughts of each period):
# ----------------------------------------------------------------------------
plt.figure(figsize=(3,3))
plt.hist(durations_list,bins=5,align='mid',rwidth=0.9)
plt.xlabel("duration")
plt.ylabel("#")
plt.title("drought durations, South West US, threshold=%d" % (pdsi_threshold))
