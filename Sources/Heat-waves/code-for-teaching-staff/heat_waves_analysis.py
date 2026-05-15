# Calculate composite fields and other analyses for heat waves
# using daily output from CESM2.
#
# Variables (CMIP5 naming) of interest:
# TREFHTMX, PSL, UBOT, VBOT, Z500, U250, V250, T500, FSNS/FSNSC (net surface SW flux/ clear-sky), 
# variables in CMIP6 naming: tasmax, psl,  uas,  vas, zg500, ua250, va250, ta500m rsds, rsus, rsdscs, rsuscs

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from netCDF4 import Dataset
import cartopy.crs as ccrs
from datetime import datetime
import matplotlib.patches as mpatches
import intake
import xarray as xr
import pandas as pd
import os
from pathlib import Path
import requests
import intake
import xarray as xr


# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'
fontsize=9
plt.rcParams['font.size'] = fontsize


# TREFHTMX, PSL, UBOT, VBOT, FSNS, FSNSC = \
#   tasmax, psl,  uas,  vas, rsds, rsus, rsdscs, rsuscs

# -----------------------
# User settings
# -----------------------
SOURCE  = "GFDL-CM4"
MEMBER  = "r1i1p1f1"
GRID    = "gr2"          # from your earlier check: only gr2 had all vars for both exps
EXPS    = ["historical", "ssp585"]

# Your variables of interest (CMIP6)
VARS_DAY   = ["tasmax", "psl", "uas", "vas", "zg", "ua", "va", "ta", "rsds", "rsus"]
VARS_CFDAY = ["rsdscs", "rsuscs"]   # clear-sky SW components live in CFday

PANGEO_CMIP6 = "https://storage.googleapis.com/cmip6/pangeo-cmip6.json"

# -----------------------
# Open Pangeo catalog once
# -----------------------
cat = intake.open_esm_datastore(PANGEO_CMIP6)

def open_one(exp, var, table_id):
    """
    Return a dataset containing only `var` for the requested selection.
    """
    sub = cat.search(
        source_id=SOURCE,
        experiment_id=exp,
        member_id=MEMBER,
        grid_label=GRID,
        table_id=table_id,
        variable_id=var,
    )
    if sub.df.empty:
        raise ValueError(f"NOT FOUND in Pangeo catalog: {SOURCE} {exp} {table_id} {GRID} {MEMBER} var={var}")

    # Convert to dataset (zarr on GCS). consolidated=True is typical for Pangeo CMIP6.
    dsd = sub.to_dataset_dict(zarr_kwargs={"consolidated": True})
    ds = next(iter(dsd.values()))
    # Keep only var, drop any other leftovers
    return ds[[var]]

def merge_vars(exp, vars_list, table_id):
    """
    Open and merge a list of variables from the same exp/table.
    """
    pieces = []
    for v in vars_list:
        ds = open_one(exp, v, table_id=table_id)
        pieces.append(ds)
        shape = tuple(ds[v].shape)
        print(f"  opened {exp:10s} {table_id:5s} {v:7s} shape={shape}")
    return xr.merge(pieces, compat="override")

# -----------------------
# Load everything
# -----------------------
datasets = {}

for exp in EXPS:
    print(f"\n=== Opening {SOURCE} {exp} GRID={GRID} MEMBER={MEMBER} ===")
    ds_day   = merge_vars(exp, VARS_DAY,   table_id="day")
    ds_cfday = merge_vars(exp, VARS_CFDAY, table_id="CFday")

    # Merge day + CFday into one dataset (they share time/lat/lon; CFday is a separate table)
    ds = xr.merge([ds_day, ds_cfday], compat="override")
    datasets[exp] = ds

# -----------------------
# Coordinates (from historical)
# -----------------------
ds0 = datasets["historical"]
# Common CMIP6 coord names are lat/lon; some models use latitude/longitude
lat_name = "lat" if "lat" in ds0.coords else ("latitude" if "latitude" in ds0.coords else None)
lon_name = "lon" if "lon" in ds0.coords else ("longitude" if "longitude" in ds0.coords else None)
if lat_name is None or lon_name is None:
    raise KeyError(f"Could not find lat/lon coords. coords={list(ds0.coords)}")

time = ds0["time"]
lat  = ds0[lat_name]
lon  = ds0[lon_name]

print("\n=== Coords (from historical merged dataset) ===")
print("time:", time.shape, "lat:", lat.shape, "lon:", lon.shape)

# -----------------------
# Derived daily fields (historical shown; repeat for ssp585 similarly)
# -----------------------
def derived_fields(ds):
    out = {}

    # Pressure-level slices (Pa). Tolerance helps in case plev is not exactly 50000/25000.
    if "plev" in ds.coords:
        out["Z500"] = ds["zg"].sel(plev=50000, method="nearest", tolerance=2000)
        out["U250"] = ds["ua"].sel(plev=25000, method="nearest", tolerance=2000)
        out["V250"] = ds["va"].sel(plev=25000, method="nearest", tolerance=2000)
        out["T500"] = ds["ta"].sel(plev=50000, method="nearest", tolerance=2000)
    else:
        print("WARNING: no 'plev' coord found; skipping Z500/U250/V250/T500 slices.")

    # Surface net SW and clear-sky net SW
    out["RSNS"]  = (ds["rsds"]   - ds["rsus"]).rename("rsns")
    out["RSNSC"] = (ds["rsdscs"] - ds["rsuscs"]).rename("rsnsc")

    return out

for exp in EXPS:
    ds = datasets[exp]
    d = derived_fields(ds)
    print(f"\n=== Derived fields ({exp}) ===")
    for k, da in d.items():
        print(f"{k:6s}: dims={da.dims} shape={da.shape}")

# If you want one combined dataset per experiment including derived vars:
for exp in EXPS:
    ds = datasets[exp]
    d = derived_fields(ds)
    datasets[exp] = xr.merge([ds, d["RSNS"].to_dataset(), d["RSNSC"].to_dataset()], compat="override")

print("\nDone. You now have:")
print("  datasets['historical'] and datasets['ssp585'] as xarray Datasets from Pangeo,")
print("  containing day vars + CFday vars + derived rsns/rsnsc (daily).")


Nt_per_member = len(dates)
ensemble_members=np.arange(2,33)
print("done reading grid information, each file has",steps_per_file \
      ,"time steps, \namounting to a total time series length of",Nt_per_member)

print(" Calculate weekly averages for Z500 and TREFHTMX...")
# calculate weekly averages for Z500 and TREFHTMX over June, July,
# August from 1920 to year_max, where year_max can be <=2100, to be
# used for workshop:

year_max=1980
heat_waves_weekly_averages_TREFHTMX = tasmax.resample(time="1W").mean()
heat_waves_weekly_averages_Z500 = Z500.resample(time="1W").mean()

print("\ndone.")


# define some functions:

import numpy as np

def date_to_decimal_year(date):
    # assume `date` is numpy.datetime64
    y = int(date.astype("datetime64[Y]").astype(int) + 1970)

    start = np.datetime64(f"{y}-01-01")
    end   = np.datetime64(f"{y+1}-01-01")

    # use seconds for stable fractional year
    date_s  = date.astype("datetime64[s]")
    start_s = start.astype("datetime64[s]")
    end_s   = end.astype("datetime64[s]")

    return y + (date_s - start_s) / (end_s - start_s)


def extract_variable_from_one_ensemble_member_one_file(variable_name,file_name,ensemble_member):
    # extract data for all files of one ensemble member, 
    dir_name="/glade/collections/cdg/data/cesmLE/CESM-CAM5-BGC-LE/atm/proc/tseries/daily/"+variable_name+"/"
    ncfile=Dataset(dir_name+file_name, 'r');
    variable=ncfile.variables[variable_name]
    return variable


def calculate_Tmax_timeseries(ensemble_member):
    """read Tmax from one ensemble member, for all years, 
       into one array. calculate Tmax averaged over the area of interest:
    """
    print(ensemble_member,", ",end="")
    # read data:
    variable_name="TREFHTMX"
    file_names=["b.e11.B20TRC5CNBDRD.f09_g16.%3.3d.cam.h1.%s.19200101-20051231.nc" % (ensemble_member,variable_name) \
               ,"b.e11.BRCP85C5CNBDRD.f09_g16.%3.3d.cam.h1.%s.20060101-20801231.nc" % (ensemble_member,variable_name) \
               ,"b.e11.BRCP85C5CNBDRD.f09_g16.%3.3d.cam.h1.%s.20810101-21001231.nc" % (ensemble_member,variable_name)]
    first_file=True
    for file_name in file_names:
        Tmax=extract_variable_from_one_ensemble_member_one_file(variable_name,file_name,ensemble_member)
        # calculate timeseries by averaging over specified lat/lon range:
        ilat=np.logical_and(lat<=40,lat>=37)
        ilon=np.logical_and(lon<=360-95,lon>=360-102)
        if first_file:
            first_file=False
            Tmax_timeseries_one_ensemble_member=np.mean(Tmax[:,ilat,ilon],axis=(1,2))
        else:
            Tmax1=np.mean(Tmax[:,ilat,ilon],axis=(1,2))
            Tmax_timeseries_one_ensemble_member=np.concatenate((Tmax_timeseries_one_ensemble_member,Tmax1))
    return Tmax_timeseries_one_ensemble_member


def calc_days_to_read_for_composite(Tmax_all_timeseries,Tmax_threshold,Ndays_threshold,year_start,year_end,monthly_composite):
    """prepare for the calculation of composites, by calculating
    which days from each file of each ensemble member should be read
    to calculate composites for heat waves.
    """

    # First, calculate a mask time series for extreme wave events:
    # defined as both above Tmax_threshold and for at least
    # Ndays_threshold days in a row

    # first, a mask indicating which days are above the temperature threshold:
    Tmax_mask_days_above_threshold=1.0*Tmax_all_timeseries
    Tmax_mask_heat_waves=0.0*Tmax_all_timeseries
    if monthly_composite != monthly_composite: # clever way of testing if monthly_composite is NaN!
        # calculate composite based on thresholds:
        Tmax_mask_days_above_threshold[Tmax_all_timeseries<Tmax_threshold]=0
        Tmax_mask_days_above_threshold[Tmax_all_timeseries>=Tmax_threshold]=1
        
        # next, a mask indicating which days are part of a heat wave event:
        iensemble_member=-1
        for ensemble_member in ensemble_members:
            iensemble_member=iensemble_member+1
            for iday in range(len(Tmax_all_timeseries[0,:])-Ndays_threshold):
                neighboring_points=range(iday-np.int64(np.floor(Ndays_threshold/2)),iday+np.int64(np.floor(Ndays_threshold/2))+1)
                if np.prod(Tmax_mask_days_above_threshold[iensemble_member,neighboring_points])>0:
                    Tmax_mask_heat_waves[iensemble_member,neighboring_points]=1
    else:
        # calculate climatology based on months in variable monthly_composite:
        iensemble_member=-1
        for ensemble_member in ensemble_members:
            iensemble_member=iensemble_member+1
            is_month_in_monthly_composite=np.zeros(len(months),dtype=bool)
            i=-1
            for month in months:
                i=i+1
                is_month_in_monthly_composite[i] = month in monthly_composite
            Tmax_mask_heat_waves[iensemble_member,is_month_in_monthly_composite]=1


    # Next, using the above mask, create ranges of indices
    # corresponding to times of heat waves in each of the three files
    # for each ensemble member. This will be used to read only the
    # needed time steps (days), and thus make reading more efficient:
    days_to_read_for_composite=[]
    years_in_input_file=[]
    iensemble_member=-1
    for ensemble_member in ensemble_members:
        iensemble_member=iensemble_member+1
        days_to_read_for_composite.append([])
        for ifile in range(3):
            if iensemble_member==0:
                years_in_input_file.append([])
            days_to_read_for_composite[iensemble_member].append(list(range(steps_per_file[ifile])))
            # get heat waves mask for this file/ ensemble member:
            if ifile==0:
                s=0
                e=steps_per_file[ifile]
            else:
                s=int(np.sum(steps_per_file[0:ifile]))
                e=np.sum(steps_per_file[0:ifile+1])
            years_in_input_file[ifile]=years[s:e]
            mask=1*Tmax_mask_heat_waves[iensemble_member,s:e]
        
            # now apply the mask to get only the indices to read for
            # this file/ ensemble member:
            for iday in range(len(mask)-1,-1,-1):
                if mask[iday]<0.9 \
                    or years_in_input_file[ifile][iday]<year_start \
                    or years_in_input_file[ifile][iday]>year_end:
                    del(days_to_read_for_composite[iensemble_member][ifile][iday])
    
    # calculate percentage of points used for the composite:
    Ndays_to_composite=getSizeOfNestedList(days_to_read_for_composite)
    Ntotal_days=0
    iensemble_member=-1
    for ensemble_member in ensemble_members:
        iensemble_member=iensemble_member+1
        for ifile in range(3):
            Ntotal_days=Ntotal_days+len(years_in_input_file[ifile][\
                            np.logical_and(years_in_input_file[ifile]<=year_end\
                                          ,years_in_input_file[ifile]>=year_start)])
    percent_days_selected=100.0*Ndays_to_composite/Ntotal_days
    print("Number of days to use for composite is %d, which is %g%% of total days."  % (Ndays_to_composite,percent_days_selected))
    
    return days_to_read_for_composite,Tmax_mask_heat_waves


def calculate_composite(variable_name,days_to_read_for_composite):
    print("calculating composite for variable=",variable_name,", ensemble_member=",end="")
    Navg=0
    iensemble_member=-1
    for ensemble_member in ensemble_members:
        iensemble_member=iensemble_member+1
        print(ensemble_member,",",end="")
        # read data:
        file_names=["b.e11.B20TRC5CNBDRD.f09_g16.%3.3d.cam.h1.%s.19200101-20051231.nc" % (ensemble_member,variable_name) \
               ,"b.e11.BRCP85C5CNBDRD.f09_g16.%3.3d.cam.h1.%s.20060101-20801231.nc" % (ensemble_member,variable_name) \
               ,"b.e11.BRCP85C5CNBDRD.f09_g16.%3.3d.cam.h1.%s.20810101-21001231.nc" % (ensemble_member,variable_name)]
        ifile=-1
        for file_name in file_names:
            ifile=ifile+1
            variable=extract_variable_from_one_ensemble_member_one_file(variable_name,file_name,ensemble_member)
            days=np.asarray(days_to_read_for_composite[iensemble_member][ifile],dtype=np.int)
            if ifile==0 and iensemble_member==0:
                if len(days)>0:
                    Navg=Navg+len(days)
                    variable_avg=np.sum(variable[days,:,:],axis=0)
            else:
                if len(days)>0:
                    Navg=Navg+len(days)
                    variable_avg=variable_avg+np.sum(variable[days,:,:],axis=0)
                
    # finalize calculation of average:
    variable_avg=variable_avg/Navg
    print("done.")
    return variable_avg


def getSizeOfNestedList(listOfElem):
    """Get number of elements in a nested list, from
    getSizeOfNestedList
    https://thispointer.com/python-get-number-of-elements-in-a-list-lists-of-lists-or-nested-list/

    """
    count = 0
    # Iterate over the list
    for elem in listOfElem:
        # Check if type of element is list
        if type(elem) == list:  
            # Again call this function to get the size of this element
            count += getSizeOfNestedList(elem)
        else:
            count += 1    
    return count


def calc_pdf_of_Tmax_time_series(Tmax_for_pdf):
    Tmax_for_pdf.reshape(np.prod(Tmax_for_pdf.shape))
    # calculate the histograms:
    Tmax_hist, Tmax_bin_edges = np.histogram(Tmax_for_pdf, bins=range(-23,49,1), density=True)
    Tmax_x=(Tmax_bin_edges[1:]+Tmax_bin_edges[0:-1])/2
    Tmax_dx=(Tmax_bin_edges[1:]-Tmax_bin_edges[0:-1])
    Tmax_cdf=np.cumsum(Tmax_hist*Tmax_dx)
    return Tmax_x, Tmax_hist, Tmax_cdf


def calc_decadal_statistics(Tmax_all_timeseries,Tmax_mask_heat_waves_composite):
    """accumulate all durations and amplitudes of Tmax heat wave 
       events and calculate timeseries of decadal statistics."""
    Ndecades=int(np.floor((years[-1]-years[0])/10))

    # initialize arrays:
    avg_Tmax_heat_waves=np.zeros(Ndecades)
    Ndays_heat_waves_per_year=np.zeros(Ndecades)
    avg_duration_heat_waves=np.zeros(Ndecades)
    num_heat_waves_per_year=np.zeros(Ndecades)
    year_decade_start=np.zeros(Ndecades)

    # calculate for each decade:
    durations=[]
    amplitudes=[]
    for idec in range(Ndecades):
        durations.append([])
        amplitudes.append([])
        year_start=years[0]+idec*10
        year_end=years[0]+(idec+1)*10
        year_decade_start[idec]=year_start+5
        # heat wave days per year:
        Ndays_heat_waves_per_year[idec]=np.nansum(Tmax_mask_heat_waves_composite[:
                ,np.logical_and(years<year_end,years>=year_start)])
        # average maximum daily temperature of heat wave days:
        tmp1=1.0*Tmax_mask_heat_waves_composite
        tmp1[tmp1==0]=np.nan
        tmp2=Tmax_all_timeseries*tmp1
        tmp3=tmp2[:,np.logical_and(years<year_end,years>=year_start)]
        avg_Tmax_heat_waves[idec]=np.nanmean(tmp3)
        amplitudes_this_decade=np.asarray(tmp3).flatten()
        amplitudes_this_decade=amplitudes_this_decade[np.logical_not(np.isnan(amplitudes_this_decade))]
        amplitudes[idec].append(amplitudes_this_decade)
        # heat wave duration and frequency:
        Tmax_mask_heat_waves_this_decade=Tmax_mask_heat_waves_composite[:
                ,np.logical_and(years<year_end,years>=year_start)]
        Ndays=len(Tmax_mask_heat_waves_this_decade[0,:])
        nevents=0
        iensemble_member=-1
        for ensemble_member in ensemble_members:
            iensemble_member=iensemble_member+1
            duration=0
            for iday in range(1,Ndays):
                if Tmax_mask_heat_waves_this_decade[iensemble_member,iday-1]==1 and \
                    Tmax_mask_heat_waves_this_decade[iensemble_member,iday]==0:
                    nevents=nevents+1
                    durations[idec].append(duration)
                    duration=0
                elif Tmax_mask_heat_waves_this_decade[iensemble_member,iday]==1:
                    duration=duration+1

        Ndays_heat_waves_per_year[idec]=Ndays_heat_waves_per_year[idec]/len(ensemble_members)/10.0
        num_heat_waves_per_year[idec]=nevents/len(ensemble_members)/10.0
        #print("idec=",idec,",durations=",durations)
        avg_duration_heat_waves[idec]=np.mean(np.asarray(durations[idec]))
    
    return year_decade_start,Ndays_heat_waves_per_year,avg_Tmax_heat_waves \
            ,avg_duration_heat_waves,num_heat_waves_per_year,durations,amplitudes


def calc_duration_and_amplitude_pdfs(durations,amplitudes):
    # calculate and plot the histograms for duration:
    durations_to_analyze = []
    for sublist in durations:
        for item in sublist:
            durations_to_analyze.append(item)
    durations_to_analyze=np.asarray(durations_to_analyze)
    dur_hist_to_analyze, dur_bin_edges_to_analyze = np.histogram(durations_to_analyze, bins=np.arange(3,20), density=True)
    dur_x_to_analyze=(dur_bin_edges_to_analyze[1:]+dur_bin_edges_to_analyze[0:-1])/2

    # calculate and plot the histograms for amplitudes:
    amplitudes_to_analyze = []
    for sublist in amplitudes:
        for item in sublist:
            for i in item:
                amplitudes_to_analyze.append(i)
    amplitudes_to_analyze=np.asarray(amplitudes_to_analyze)
    amp_hist_to_analyze, amp_bin_edges_to_analyze = np.histogram(amplitudes_to_analyze-273.15, bins=np.arange(39,50), density=True)
    amp_x_to_analyze=(amp_bin_edges_to_analyze[1:]+amp_bin_edges_to_analyze[0:-1])/2

    return dur_hist_to_analyze, dur_x_to_analyze, amp_hist_to_analyze, amp_x_to_analyze


print("functions defined.")

# calculate month and year for each day in the record, and plot all
# Tmax time series: dates to decimal years:
years=np.zeros(Nt_per_member)
months=np.zeros(Nt_per_member)
idate=-1
for date in dates:
    idate=idate+1
    years[idate]=date_to_decimal_year(date)
    months[idate]=dates[idate].month

months=months.astype(int)
print("calculated years and months time series.")

# calculate and plot a time series of averaged total precipitation
# over california as function of time:
Tmax_all_timeseries=np.zeros((len(ensemble_members),Nt_per_member))
print("calculate_Tmax_timeseries, ensemble_member=",end="")
iensemble_member=-1
for ensemble_member in ensemble_members:
    iensemble_member=iensemble_member+1
    Tmax_all_timeseries[iensemble_member,:]=calculate_Tmax_timeseries(ensemble_member)

# save to file:
np.save("Output/heat_waves_Tmax_all_timeseries.npy",Tmax_all_timeseries)


print("done.")

# calc avereage over all ensemble members:
Tmax_timeseries_avg=np.mean(Tmax_all_timeseries[:,:],axis=0)

# plot Tmax timeseries
fig=plt.figure(dpi=300,figsize=(4,6))
plt.clf()

plt.subplot(3,1,1)
iensemble_member=-1
for ensemble_member in ensemble_members:
    iensemble_member=iensemble_member+1
    plt.plot(years,Tmax_all_timeseries[iensemble_member,:]-273.15,lw=0.25,alpha=0.4)
plt.plot(years,Tmax_timeseries_avg-273.15,lw=0.4,color='b',label="mean")
#plt.xlabel("year")
plt.ylabel("$T_{\\rm max}$ ($^\\circ$C)")
ax=plt.gca()
ax.set_xticks(range(1920,2100,1), minor=True)
#ax.set_yticks(range(260,300,1), minor=True)
plt.xlim([1920,1925]);
plt.ylim([10,47]);
plt.legend()
plt.grid(lw=0.25);

plt.subplot(3,1,2)
iensemble_member=-1
for ensemble_member in ensemble_members:
    iensemble_member=iensemble_member+1
    plt.plot(years,Tmax_all_timeseries[iensemble_member,:]-273.15,lw=0.25,alpha=0.4)
plt.plot(years,Tmax_timeseries_avg-273.15,lw=0.4,color='b',label="mean")
#plt.xlabel("year")
plt.ylabel("$T_{\\rm max}$ ($^\\circ$C)")
ax=plt.gca()
ax.set_xticks(range(1920,2100,1), minor=True)
#ax.set_yticks(range(260,300,1), minor=True)
plt.xlim([2000,2005]);
plt.ylim([10,47]);
plt.legend()
plt.grid(lw=0.25);

plt.subplot(3,1,3)
iensemble_member=-1
for ensemble_member in ensemble_members:
    iensemble_member=iensemble_member+1
    plt.plot(years,Tmax_all_timeseries[iensemble_member,:]-273.15,lw=0.25,alpha=0.4)
plt.plot(years,Tmax_timeseries_avg-273.15,lw=0.4,color='b',label="mean")
plt.xlabel("Year")
plt.ylabel("$T_{\\rm max}$ ($^\\circ$C)")
ax=plt.gca()
ax.set_xticks(range(1920,2100,1), minor=True)
#ax.set_yticks(range(260,300,1), minor=True)
plt.xlim([2095,2100]);
plt.ylim([10,47]);
plt.legend()
plt.grid(lw=0.25);


plt.tight_layout()
plt.show();

# %%
# prepare for calculating composites:

# first, calculate which days should be composited by specifying 
# the parameters of the heat wave and the years of interest:
Tmax_threshold=273.15+39
Ndays_threshold=3 # make this an odd number

# days to read for summer climatology:
year_start=1920
year_end=1960
monthly_composite=[8] # month number or nan for using above thresholds
print("for Climatology:")
days_to_read_for_climatology,Tmax_mask_heat_waves_climatology=\
   calc_days_to_read_for_composite(Tmax_all_timeseries,Tmax_threshold,Ndays_threshold,year_start,year_end,monthly_composite)

# days to read for heat wave composites:
monthly_composite=np.nan # month number or nan for using above thresholds
year_start=1920
year_end=1960
monthly_composite=np.nan
print("for heat wave composites:")
days_to_read_for_composite,Tmax_mask_heat_waves_composite=\
   calc_days_to_read_for_composite(Tmax_all_timeseries,Tmax_threshold,Ndays_threshold,year_start,year_end,monthly_composite)


# plot timeseries and mask for one ensemble member to verify:
plt.figure(figsize=(5,3),dpi=300)
iensemble_member=0
plt.plot(years,Tmax_all_timeseries[iensemble_member,:],lw=0.25,alpha=0.4,label="Tmax")
mask_climatology=1.0*Tmax_mask_heat_waves_climatology
mask_composite=1.0*Tmax_mask_heat_waves_composite
mask_composite[mask_composite<0.9]=np.nan
mask_climatology[mask_climatology<0.9]=np.nan
plt.plot(years,mask_composite[iensemble_member,:]+Tmax_threshold-1,'.',markersize=0.25,lw=0.25,color="r",label="mask composite")
plt.plot(years,mask_climatology[iensemble_member,:]+Tmax_threshold-2,'.',markersize=0.1,lw=0.25,color="b",label="mask climatology")
plt.grid(lw=0.25)
plt.legend()
plt.xlim([2095,2100]);
plt.tight_layout()

# %%
# now calculate the composites:

variable_name="PSL"
PSL_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="PSL"
PSL_composite=calculate_composite(variable_name,days_to_read_for_composite)

variable_name="TREFHTMX"
Tmax_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="TREFHTMX"
Tmax_composite=calculate_composite(variable_name,days_to_read_for_composite)

variable_name="Z500"
Z500_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="Z500"
Z500_composite=calculate_composite(variable_name,days_to_read_for_composite)

variable_name="UBOT"
UBOT_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="UBOT"
UBOT_composite=calculate_composite(variable_name,days_to_read_for_composite)

variable_name="VBOT"
VBOT_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="VBOT"
VBOT_composite=calculate_composite(variable_name,days_to_read_for_composite)

variable_name="U250"
U250_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="U250"
U250_composite=calculate_composite(variable_name,days_to_read_for_composite)

variable_name="V250"
V250_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="V250"
V250_composite=calculate_composite(variable_name,days_to_read_for_composite)

variable_name="FSNSC"
FSNSC_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

variable_name="FSNSC"
FSNSC_composite=calculate_composite(variable_name,days_to_read_for_composite)

print("done.")

# save for students:
np.save("Output/heat_waves_composite_Tmax.npy",np.asarray(Tmax_composite))
np.save("Output/heat_waves_composite_PSL.npy",np.asarray(PSL_composite))
np.save("Output/heat_waves_composite_Z500.npy",np.asarray(Z500_composite))
np.save("Output/heat_waves_composite_U250.npy",np.asarray(U250_composite))
np.save("Output/heat_waves_composite_V250.npy",np.asarray(V250_composite))
np.save("Output/heat_waves_composite_UBOT.npy",np.asarray(VBOT_composite))
np.save("Output/heat_waves_composite_VBOT.npy",np.asarray(VBOT_composite))
np.save("Output/heat_waves_composite_FSNSC.npy",np.asarray(FSNSC_composite))
np.save("Output/heat_waves_climatology_Tmax.npy",np.asarray(Tmax_climatology))
np.save("Output/heat_waves_climatology_PSL.npy",np.asarray(PSL_climatology))
np.save("Output/heat_waves_climatology_Z500.npy",np.asarray(Z500_climatology))
np.save("Output/heat_waves_climatology_U250.npy",np.asarray(U250_climatology))
np.save("Output/heat_waves_climatology_V250.npy",np.asarray(V250_climatology))
np.save("Output/heat_waves_climatology_UBOT.npy",np.asarray(UBOT_climatology))
np.save("Output/heat_waves_climatology_VBOT.npy",np.asarray(VBOT_climatology))
np.save("Output/heat_waves_climatology_FSNSC.npy",np.asarray(FSNSC_climatology))
np.save("Output/heat_waves_lon.npy",lon)
np.save("Output/heat_waves_lat.npy",lat)
np.save("Output/heat_waves_ensemble_members.npy",ensemble_members)
np.save("Output/heat_waves_ensemble_members_dates.npy",dates)
print("done.")

# draw composites minus climatologies:

# for \text command to work: (latex only works on my laptop)
plt.rcParams['text.usetex'] = False

# add a column to lon/lat arrays to eliminate white gap at dateline:
# for atmospheric plots:
lon1=1.0*lon[-1]+lon[2]-lon[1]; lon1=np.hstack((lon,lon1))

# initialize figure:
plt.clf();
projection=ccrs.PlateCarree(central_longitude=0.0);
fig,axes=plt.subplots(2,2,figsize=(5.6,2.5),dpi=300,subplot_kw={'projection': projection});
s=3 # skip arrows in quiver plots
shrink=0.95
lon_min=190
lon_max=330.
lat_min=19.99
lat_max=81.001
# for textboxes with (a), (b) etc:
props = dict(boxstyle='round', edgecolor="wheat", facecolor='wheat', alpha=0.9)

# Tmax:
# -----
if 1:
    #axes[0,0].set_extent([0, 359.99, -90, 90], crs=ccrs.PlateCarree())
    axes[0,0].set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    axes[0,0].coastlines(resolution='110m',lw=0.3)
    plt.set_cmap('bwr')
    #axes[0,0].gridlines(lw=0.2)
    DATA=1.0*(Tmax_composite-Tmax_climatology)
    DATA2a_tmp=1.0*(UBOT_composite-0*UBOT_climatology)
    DATA2b_tmp=1.0*(VBOT_composite-0*VBOT_climatology)
    # add row to data to eliminate white gap at dateline:
    DATA1=1.0*DATA[:,0]; DATA1.shape=(len(DATA1[:]),1); DATA1=np.hstack((DATA,DATA1))
    DATA2a=1.0*DATA2a_tmp[:,0]; DATA2a.shape=(len(DATA2a[:]),1); DATA2a=np.hstack((DATA2a_tmp,DATA2a))
    DATA2b=1.0*DATA2b_tmp[:,0]; DATA2b.shape=(len(DATA2b[:]),1); DATA2b=np.hstack((DATA2b_tmp,DATA2b))
    levels=np.arange(-12,12.1,0.1)
    c=axes[0,0].contourf(lon1,lat, DATA1[:,:],levels=levels)
    clb=plt.colorbar(c, shrink=shrink, pad=0.02,ax=axes[0,0],ticks=range(-12,15,4))
    clb.ax.yaxis.set_tick_params(pad=2)
    clb.set_label('K',labelpad=1)
    arrow_scale=200
    hq=axes[0,0].quiver(lon1[::s],lat[::s],DATA2a[::s,::s],DATA2b[::s,::s],scale=arrow_scale)
    # add a scale vector, first a rectangular white background
    axes[0,0].add_patch(mpatches.Rectangle(xy=[0.02, 0.03], width=0.2, height=0.17 \
                ,edgecolor="w", lw=0.01, facecolor='w',transform=axes[0,0].transAxes))
    hqk=axes[0,0].quiverkey(hq, X=0.12, Y=0.05, U=10,label="10 m/s",labelsep=0.02,coordinates='axes')
    axes[0,0].set_title('(a) $T_{max}$, $[u_s,v_s]$',pad=1,loc="left",fontsize=fontsize)
    axes[0,0].add_patch(mpatches.Rectangle(xy=[360-102, 37], width=7, height=3
                ,edgecolor="w", lw=0.5, facecolor='none',transform=ccrs.PlateCarree()))
    gl = axes[0,0].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.25, color='gray', alpha=0.5, linestyle='-')
    gl.xlocator = mticker.FixedLocator(np.arange(-160,0,40))
    gl.ylocator = mticker.FixedLocator(np.arange(20,100,20))
    gl.left_labels = True
    gl.right_labels = False
    gl.top_labels = False
    gl.bottom_labels = False
    gl.ypadding=2
    gl.xpadding=3

# PSL:
# -----------------
if 1:
    #axes[0,1].set_extent([0, 359.99, -90, 90], crs=ccrs.PlateCarree())
    axes[0,1].set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    axes[0,1].coastlines(resolution='110m',lw=0.3)
    #plt.set_cmap('viridis')
    plt.set_cmap('bwr')
    #axes[0].gridlines(lw=0.2)
    DATA_tmp=1.0*(PSL_composite-PSL_climatology)/100
    DATA2a_tmp=1.0*(UBOT_composite-UBOT_climatology)
    DATA2b_tmp=1.0*(VBOT_composite-VBOT_climatology)
    # add row to data to eliminate white gap at dateline:
    DATA1 =1.0*DATA_tmp[:,0];   DATA1.shape= (len(DATA1[:]),1);  DATA1 =np.hstack((DATA_tmp,DATA1))
    DATA2a=1.0*DATA2a_tmp[:,0]; DATA2a.shape=(len(DATA2a[:]),1); DATA2a=np.hstack((DATA2a_tmp,DATA2a))
    DATA2b=1.0*DATA2b_tmp[:,0]; DATA2b.shape=(len(DATA2b[:]),1); DATA2b=np.hstack((DATA2b_tmp,DATA2b))
    levels=np.arange(-6,6.1,0.1)
    c=axes[0,1].contourf(lon1,lat, DATA1[:,:],levels)
    clb=plt.colorbar(c, shrink=shrink, pad=0.02,ax=axes[0,1],ticks=range(-6,8,2))
    clb.ax.yaxis.set_tick_params(pad=2)
    clb.set_label('hPa',labelpad=2)
    arrow_scale=50
    hq=axes[0,1].quiver(lon1[::s],lat[::s],DATA2a[::s,::s],DATA2b[::s,::s],scale=arrow_scale)
    # add a scale vector, first a rectangular white background
    axes[0,1].add_patch(mpatches.Rectangle(xy=[0.02, 0.03], width=0.2, height=0.17 \
                ,edgecolor="w", lw=0.01, facecolor='w',transform=axes[0,1].transAxes))
    hqk=axes[0,1].quiverkey(hq, X=0.12, Y=0.05, U=2,label="2 m/s",labelsep=0.02,coordinates='axes')
    axes[0,1].set_title('(b) $P_{{sea-level}}$, $[u_s^\\prime,v_s^\\prime]$',pad=4,loc="left",fontsize=fontsize)
    axes[0,1].add_patch(mpatches.Rectangle(xy=[360-102, 37], width=7, height=3
                ,edgecolor="w", lw=0.5, facecolor='none',transform=ccrs.PlateCarree()))
    gl = axes[0,1].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.25, color='gray', alpha=0.5, linestyle='-')
    gl.xlocator = mticker.FixedLocator(np.arange(-160,0,40))
    gl.ylocator = mticker.FixedLocator(np.arange(20,100,20))
    gl.left_labels = False
    gl.right_labels = False
    gl.top_labels = False
    gl.bottom_labels = False


    
# Z500: 
# -----
if 1:
    #axes[1,0].set_extent([0, 359.99, -90, 90], crs=ccrs.PlateCarree())
    axes[1,0].set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    axes[1,0].coastlines(resolution='110m',lw=0.3)
    #plt.set_cmap('viridis')
    plt.set_cmap('bwr')
    #axes[1,0].gridlines(lw=0.2)
    DATA=1.0*(Z500_composite-Z500_climatology)
    DATA2a_tmp=1.0*(U250_composite-0*U250_climatology)
    DATA2b_tmp=1.0*(V250_composite-0*V250_climatology)
    # add row to data to eliminate white gap at dateline:
    DATA1=1.0*DATA[:,0]; DATA1.shape=(len(DATA1[:]),1); DATA1=np.hstack((DATA,DATA1))
    DATA2a=1.0*DATA2a_tmp[:,0]; DATA2a.shape=(len(DATA2a[:]),1); DATA2a=np.hstack((DATA2a_tmp,DATA2a))
    DATA2b=1.0*DATA2b_tmp[:,0]; DATA2b.shape=(len(DATA2b[:]),1); DATA2b=np.hstack((DATA2b_tmp,DATA2b))
    levels=np.arange(-55,56,1)
    c=axes[1,0].contourf(lon1,lat, DATA1[:,:],levels=levels)
    clb=plt.colorbar(c, shrink=shrink, pad=0.02,ax=axes[1,0],ticks=range(-50,60,20))
    clb.ax.yaxis.set_tick_params(pad=2)
    clb.set_label('m',labelpad=1)
    arrow_scale=500
    hq=axes[1,0].quiver(lon1[::s],lat[::s],DATA2a[::s,::s],DATA2b[::s,::s],scale=arrow_scale)
    # add a scale vector, first a rectangular white background
    axes[1,0].add_patch(mpatches.Rectangle(xy=[0.02, 0.03], width=0.2, height=0.17 \
                ,edgecolor="w", lw=0.01, facecolor='w',transform=axes[1,0].transAxes))
    hqk=axes[1,0].quiverkey(hq, X=0.12, Y=0.05, U=20,label="20 m/s",labelsep=0.02,coordinates='axes')
    axes[1,0].set_title('(c) $z(500~{hPa}),~[u, v]~(250~{hPa})$',pad=0,loc="left",fontsize=fontsize)
    axes[1,0].add_patch(mpatches.Rectangle(xy=[360-102, 37], width=7, height=3
                ,edgecolor="w", lw=0.5, facecolor='none',transform=ccrs.PlateCarree()))
    gl = axes[1,0].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.25, color='gray', alpha=0.5, linestyle='-')
    gl.xlocator = mticker.FixedLocator(np.arange(-160,0,40))
    gl.ylocator = mticker.FixedLocator(np.arange(20,100,20))
    gl.left_labels = True
    gl.right_labels = False
    gl.top_labels = False
    gl.bottom_labels = True
    gl.ypadding=2
    gl.xpadding=3


# FSNS: 
# -----
if 1:
    #axes[1,1].set_extent([0, 359.99, -90, 90], crs=ccrs.PlateCarree())
    axes[1,1].set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    axes[1,1].coastlines(resolution='110m',lw=0.3)
    #plt.set_cmap('viridis')
    plt.set_cmap('bwr')
    #axes[1,1].gridlines(lw=0.2)
    DATA=1.0*(Z500_composite-Z500_climatology)
    DATA2a_tmp=1.0*(U250_composite-U250_climatology)
    DATA2b_tmp=1.0*(V250_composite-V250_climatology)
    # add row to data to eliminate white gap at dateline:
    DATA1=1.0*DATA[:,0]; DATA1.shape=(len(DATA1[:]),1); DATA1=np.hstack((DATA,DATA1))
    DATA2a=1.0*DATA2a_tmp[:,0]; DATA2a.shape=(len(DATA2a[:]),1); DATA2a=np.hstack((DATA2a_tmp,DATA2a))
    DATA2b=1.0*DATA2b_tmp[:,0]; DATA2b.shape=(len(DATA2b[:]),1); DATA2b=np.hstack((DATA2b_tmp,DATA2b))
    levels=np.arange(-55,55.1,0.1)
    c=axes[1,1].contourf(lon1,lat, DATA1[:,:],levels=levels)
    clb=plt.colorbar(c, shrink=shrink, pad=0.02,ax=axes[1,1],ticks=range(-50,60,20))
    clb.ax.yaxis.set_tick_params(pad=2)
    clb.set_label('W/m$^2$',labelpad=2)
    arrow_scale=250
    hq=axes[1,1].quiver(lon1[::s],lat[::s],DATA2a[::s,::s],DATA2b[::s,::s],scale=arrow_scale)
    # add a scale vector, first a rectangular white background
    axes[1,1].add_patch(mpatches.Rectangle(xy=[0.02, 0.03], width=0.2, height=0.17 \
                ,edgecolor="w", lw=0.01, facecolor='w',transform=axes[1,1].transAxes))
    hqk=axes[1,1].quiverkey(hq, X=0.12, Y=0.05, U=10,label="10 m/s",labelsep=0.02,coordinates='axes')
    axes[1,1].set_title('(d) Net surface SW, $[u^\\prime, v^\\prime]~(250~{hPa})$',pad=3,loc="left",fontsize=fontsize)
    axes[1,1].add_patch(mpatches.Rectangle(xy=[360-102, 37], width=7, height=3
                ,edgecolor="w", lw=0.5, facecolor='none',transform=ccrs.PlateCarree()))
    gl = axes[1,1].gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0.25, color='gray', alpha=0.5, linestyle='-')
    gl.xlocator = mticker.FixedLocator(np.arange(-160,0,40))
    gl.ylocator = mticker.FixedLocator(np.arange(20,100,20))
    gl.left_labels = False
    gl.right_labels = False
    gl.top_labels = False
    gl.bottom_labels = True
    gl.ypadding=2
    gl.xpadding=3


# finalize and show plot:
plt.subplots_adjust(top=0.92, bottom=0.08, left=0.06, right=0.97, hspace=0.3,wspace=0.07);
plt.show();
fig.savefig("Output/heat-waves-composites.pdf");

# %%
# plot time series of decadal statistics:
# ---------------------------------------

year_decade_start,Ndays_heat_waves_per_year,avg_Tmax_heat_waves \
    ,avg_duration_heat_waves,num_heat_waves_per_year,durations,amplitudes\
    =calc_decadal_statistics(Tmax_all_timeseries,Tmax_mask_heat_waves_composite)


# for textboxes with (a), (b) etc:
props = dict(boxstyle='round', edgecolor="wheat", facecolor='wheat', alpha=0.9)

fig=plt.figure(figsize=(6,4),dpi=300)
plt.subplot(2,2,1)
plt.plot(year_decade_start,Ndays_heat_waves_per_year)
plt.ylabel("\\# days/year")
#plt.xlabel("Year");
plt.xlim(1920,2100)
plt.grid(lw=0.25)
axes=plt.gca()
plt.text(0.05, 0.94, "(a)", transform=axes.transAxes,
        verticalalignment='top', bbox=props)

plt.subplot(2,2,2)
plt.plot(year_decade_start,avg_Tmax_heat_waves-273.15)
plt.ylabel("$\\langle T_{\\rm max}\\rangle$, ($^\\circ$C)")
#plt.xlabel("year");
plt.xlim(1920,2100)
plt.grid(lw=0.25)
axes=plt.gca()
plt.text(0.05, 0.94, "(b)", transform=axes.transAxes,
        verticalalignment='top', bbox=props)

plt.subplot(2,2,3)
plt.plot(year_decade_start,num_heat_waves_per_year)
plt.ylabel("\\# events/year")
plt.xlabel("Year");
plt.xlim(1920,2100)
plt.grid(lw=0.25)
axes=plt.gca()
plt.text(0.05, 0.94, "(c)", transform=axes.transAxes,
        verticalalignment='top', bbox=props)

plt.subplot(2,2,4)
plt.plot(year_decade_start,avg_duration_heat_waves)
plt.ylabel("Averaged duration")
plt.xlabel("Year");
plt.xlim(1920,2100)
plt.grid(lw=0.25)
axes=plt.gca()
plt.text(0.05, 0.94, "(d)", transform=axes.transAxes,
        verticalalignment='top', bbox=props)

plt.tight_layout()
plt.show();


# %%
# calculate pdfs of Tmax, duration and amplitude for first and last decades, 
# and for first decades plus a temperature shift:
# ---------------------------------------------------------------------

# calculate shift between first and last decades:
Tmax_shift=np.mean(Tmax_all_timeseries[:,years>=2060])-np.mean(Tmax_all_timeseries[:,years<=1960])
print("Tmax_shift=",Tmax_shift)

print("First, using original Tmax time series:")
# prepare for calculation:
#summer_months=np.logical_and(np.logical_and(months==6,months==7),months==8)
monthly_composite=np.nan # nan for an actual composite, rather than climatology

days_to_read_for_composite,Tmax_mask_heat_waves_composite=\
   calc_days_to_read_for_composite(Tmax_all_timeseries,Tmax_threshold,Ndays_threshold,year_start,year_end,monthly_composite)
year_decade_start,Ndays_heat_waves_per_year,avg_Tmax_heat_waves \
    ,avg_duration_heat_waves,num_heat_waves_per_year,durations,amplitudes\
    =calc_decadal_statistics(Tmax_all_timeseries,Tmax_mask_heat_waves_composite)

# calculate pdfs:
Tmax_x_until1960,Tmax_hist_until1960,Tmax_cdf_until1960 \
    =calc_pdf_of_Tmax_time_series(1.0*Tmax_all_timeseries[:,years<=1960]-273.15)
Tmax_x_post2060,Tmax_hist_post2060,Tmax_cdf_post2060 \
    =calc_pdf_of_Tmax_time_series(1.0*Tmax_all_timeseries[:,years>=2060]-273.15)
dur_hist_until1960, dur_x_until1960, amp_hist_until1960, amp_x_until1960\
    =calc_duration_and_amplitude_pdfs(durations[0:4],amplitudes[0:4])
dur_hist_post2060, dur_x_post2060, amp_hist_post2060, amp_x_post2060\
    =calc_duration_and_amplitude_pdfs(durations[-4:],amplitudes[-4:])

print("Then, for shifted time series of first few decades:")
days_to_read_for_composite_shifted,Tmax_mask_heat_waves_composite_shifted \
   =calc_days_to_read_for_composite(Tmax_all_timeseries+Tmax_shift,Tmax_threshold \
                                    ,Ndays_threshold,year_start,year_end,monthly_composite)
year_decade_start_shifted,Ndays_heat_waves_per_year_shifted,avg_Tmax_heat_waves_shifted \
    ,avg_duration_heat_waves_until1960_shifted,num_heat_waves_per_year_until1960_shifted \
    ,durations_until1960_shifted,amplitudes_until1960_shifted \
    =calc_decadal_statistics(Tmax_all_timeseries+Tmax_shift,Tmax_mask_heat_waves_composite_shifted)
Tmax_x_until1960_shifted,Tmax_hist_until1960_shifted,Tmax_cdf_until1960_shifted \
    =calc_pdf_of_Tmax_time_series(1.0*Tmax_all_timeseries[:,years<=1960]+Tmax_shift-273.15)
dur_hist_until1960_shifted, dur_x_until1960_shifted, amp_hist_until1960_shifted, amp_x_until1960_shifted\
    =calc_duration_and_amplitude_pdfs(durations_until1960_shifted[0:4],amplitudes_until1960_shifted[0:4])

# %%
# bar plots of all pdfs:

# Tmax pdfs:
fig=plt.figure(figsize=(7,2.7),dpi=300)
plt.subplot(1,3,1)
h1=plt.bar(Tmax_x_until1960,Tmax_hist_until1960,color="b",label="1920–1960");
h2=plt.bar(Tmax_x_post2060,Tmax_hist_post2060,color="r",alpha=0.6,label="2060–2100");
h3,=plt.plot(Tmax_x_until1960_shifted,Tmax_hist_until1960_shifted,color="g" \
         ,drawstyle='steps',label="Shifted");
plt.xlabel("$T_{\\rm max}$ (°C)")
plt.ylabel("PDF")
plt.grid(lw=0.25);
ax=plt.gca();
ax.set_xticks(range(-0,50,1), minor=True)
plt.xlim(-20,48)
hh=[h1,h2,h3]
#plt.legend(hh,[H.get_label() for H in hh])
plt.title("(a)",loc="left")


# save some variables to be plotted for introduction chapter:
np.save("Output/Tmax_x_until1960.npy",Tmax_x_until1960)
np.save("Output/Tmax_hist_until1960.npy",Tmax_hist_until1960)
np.save("Output/Tmax_x_post2060.npy",Tmax_x_post2060)
np.save("Output/Tmax_hist_post2060.npy",Tmax_hist_post2060)

# durations pdfs:
plt.subplot(1,3,2)
h1=plt.bar(dur_x_until1960,dur_hist_until1960,color="b",label="1920–1960");
h2=plt.bar(dur_x_post2060,dur_hist_post2060,color="r",alpha=0.6,label="2060–2100");
x=dur_x_until1960_shifted+(dur_x_until1960_shifted[1]-dur_x_until1960_shifted[0])/2.0
y=1.0*dur_hist_until1960_shifted
x1=np.hstack((x[0]-(x[1]-x[0]),x))
y1=np.hstack((y[0],y))
h3,=plt.plot(x1,y1,color="g",drawstyle='steps',label="Shifted");
plt.xlabel("Duration (days)")
#plt.ylabel("PDF")
plt.grid(lw=0.25);
ax=plt.gca();
#ax.set_xticks(range(250,350,1), minor=True)
#plt.xlim(250,320)
hh=[h1,h2,h3]
plt.legend(hh,[H.get_label() for H in hh])
plt.title("(b)",loc="left")


# amplitudes pdfs:
plt.subplot(1,3,3)
h1=plt.bar(amp_x_until1960,amp_hist_until1960,color="b",label="1920–1960");
h2=plt.bar(amp_x_post2060,amp_hist_post2060,color="r",alpha=0.6,label="2060–2100");
x=amp_x_until1960_shifted+(amp_x_until1960_shifted[1]-amp_x_until1960_shifted[0])/2.0
y=1.0*amp_hist_until1960_shifted
x1=np.hstack((x[0]-(x[1]-x[0]),x))
y1=np.hstack((y[0],y))
h3,=plt.plot(x1,y1,color="g",drawstyle='steps',label="Shifted");
plt.xlabel("$T_{\\rm max}$ (°C)")
#plt.ylabel("PDF")
plt.grid(lw=0.25);
ax=plt.gca();
ax.set_xticks(range(38,52,1), minor=True)
plt.xlim(38,50)
hh=[h1,h2,h3]
#plt.legend(hh,[H.get_label() for H in hh])
plt.title("(c)",loc="left")

plt.tight_layout()
fig.savefig("Output/heat-waves-Tmax-duration-amplitude-PDFs.pdf");

# %%
# print and plot Tmax CDFs:

print("Tmax_x_until1960[i], Tmax_x_post2060[i], Tmax_x_until1960_shifted[i], Tmax_cdf_until1960[i], "+
      "Tmax_cdf_post2060[i],Tmax_cdf_until1960_shifted[i]")
for i in range(len(Tmax_x_until1960)):
    print(6*" % 10.6f," %(Tmax_x_until1960[i], Tmax_x_post2060[i], Tmax_x_until1960_shifted[i], \
                          100*Tmax_cdf_until1960[i], 100*Tmax_cdf_post2060[i], 100*Tmax_cdf_until1960_shifted[i]))

# plot
fig=plt.figure(figsize=(5,2.5),dpi=300)
h1=plt.bar(Tmax_x_until1960,Tmax_cdf_until1960,color="b",label="1920–1960");
h2=plt.bar(Tmax_x_post2060,Tmax_cdf_post2060,color="r",alpha=0.6,label="2060–2100");
h3,=plt.plot(Tmax_x_until1960_shifted,Tmax_cdf_until1960_shifted,color="g" \
         ,drawstyle='steps',label="Shifted");
plt.xlabel("$T_{\\rm max}$ (°C)")
plt.ylabel("CDF")
plt.grid(lw=0.25);
ax=plt.gca();
ax.set_xticks(range(-0,50,1), minor=True)
plt.xlim(-10,48)
hh=[h1,h2,h3]
plt.legend(hh,[H.get_label() for H in hh])
plt.tight_layout()
plt.show()
fig.savefig("Output/heat-waves-Tmax-CDFs.pdf");

# plot T500:

if 0:
    variable_name="T500"
    T500_climatology=calculate_composite(variable_name,days_to_read_for_climatology)

    variable_name="T500"
    T500_composite=calculate_composite(variable_name,days_to_read_for_composite)

    lon_min=190
    lon_max=330.
    lat_min=20
    lat_max=90
    lon1=1.0*lon[-1]+lon[2]-lon[1]; lon1=np.hstack((lon,lon1))
    projection=ccrs.PlateCarree(central_longitude=0.0);
    fig,axes=plt.subplots(1,1,figsize=(7,5.25),dpi=300,subplot_kw={'projection': projection});
    #axes[0,0].set_extent([0, 359.99, -90, 90], crs=ccrs.PlateCarree())
    axes.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    axes.coastlines(resolution='110m',lw=0.3)
    plt.set_cmap('bwr')
    DATA=1.0*(T500_composite-T500_climatology)
    # add row to data to eliminate white gap at dateline:
    DATA1=1.0*DATA[:,0]; DATA1.shape=(len(DATA1[:]),1); DATA1=np.hstack((DATA,DATA1))
    levels=np.arange(-2.5,2.52,0.02)
    c=axes.contourf(lon1,lat, DATA1[:,:],levels=levels)
    clb=plt.colorbar(c, shrink=0.5, pad=0.02,ax=axes)
    clb.set_label('K')
    axes.set_title('T500')

print("done.")
