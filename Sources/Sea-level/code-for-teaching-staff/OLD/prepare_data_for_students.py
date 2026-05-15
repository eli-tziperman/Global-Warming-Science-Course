import numpy as np
import pickle
from netCDF4 import Dataset as nc
import scipy
from scipy import interpolate

# ---------------------------------------------------------------
# read ocean grid cell area used for calculating global averages:
# ---------------------------------------------------------------
ncfile=nc("../../../Data-for-teaching-staff/Sea-level/areacello_fx_CCSM4_historicalNat_r0i0p0.nc",'r')  
areacello=np.asarray(ncfile.variables['areacello'][:])

# ------------------------------------------------------------------------
# read maps of SSH and ocean temperature data from NCAR CMIP5 CCSM4 model:
# ------------------------------------------------------------------------
scenario=['historical','rcp85'];
time_span=['185001-200512','200601-210012'];
time_span_theta=['185001-185912','209001-210012']
zos_filenames=["../../../Data-for-teaching-staff/Sea-level/zos_historical.nc"
              ,"../../../Data-for-teaching-staff/Sea-level/zos_rcp85.nc"]
temperature_filenames= \
    ["../../../Data-for-teaching-staff/Sea-level/thetao_historical.nc"
    ,"../../../Data-for-teaching-staff/Sea-level/thetao_rcp85.nc"]
    
Nts=[156,95]
startyears=[1850,2006]
endyears=[2005,2100]
for n in range(len(scenario)):
    exp=scenario[n]
    print("scenario = ",scenario[n])
    period=time_span[n]
    Nt=Nts[n]
    startyear=startyears[n]
    endyear=endyears[n]
    zos_filename=zos_filenames[n]
    ncfile=nc(zos_filename,'r')  # open the nc file and read data
    sealevel_lon=np.asarray(ncfile.variables['lon'][:])
    sealevel_lat=np.asarray(ncfile.variables['lat'][:])
    sealevel=np.asarray(ncfile.variables['zos'][:])

    sealevel_years=np.linspace(startyear,endyear,Nt) # only year numbers

    # apply land mask so that values over land are NaNs:
    sealevel[sealevel>1.0e10]=np.nan


    # interpolate to regular lon/lat grid, to make plotting easier for students:
    # --------------------------------------------------------------------------
    print("interpolating sea level to regular lon/lat grid for all years...")
    lon1=np.arange(0.5,360.5,1)
    lat1=np.arange(-89.5,90.5,1)
    points=np.vstack((sealevel_lon.flatten(),sealevel_lat.flatten()))
    sealevel_regular_grid_lon,sealevel_regular_grid_lat=np.meshgrid(lon1,lat1)
    Ny,Nx=sealevel_regular_grid_lon.shape
    Nyears=len(sealevel[:,0,0])
    sealevel_regular_grid=np.zeros((Nyears,Ny,Nx))
    for i in range(Nyears):
        print("year = ",sealevel_years[i])
        values=sealevel[i,:,:].flatten()
        sealevel_regular_grid[i,:,:]=scipy.interpolate.griddata(points.T,values
                                   ,(sealevel_regular_grid_lon,sealevel_regular_grid_lat)
                                   ,method='linear')
    print("    done.")

    # calculate areacello for interpolated regular grid:
    pi=3.14159265
    R_earth=6378000.0
    areacello=np.cos(sealevel_regular_grid_lat*pi/180)*R_earth**2
    areacello[np.isnan(sealevel_regular_grid[0,:,:])]=np.nan

    # also take the difference between sea water temperature
    period=time_span_theta[n]
    # data are originally from:
    # '/glade/collections/cmip/cmip5/output1/NCAR/CCSM4/'+exp+'/mon/ocean/Omon/r6i1p1/v20140820/thetao/'
    
    ncfile=nc(temperature_filenames[n],'r')
    Temperature_ocean_lev=np.asarray(ncfile.variables['lev'][:])
    Temperature_ocean_lat=np.asarray(ncfile.variables['lat'][:])
    Temperature_ocean_lon=np.asarray(ncfile.variables['lon'][:])   
    Temperature_ocean=np.asarray(ncfile.variables['thetao'][:])
    # apply land mask:
    Temperature_ocean[Temperature_ocean>1.0e10]=np.nan

    # interpolate to regular lon/lat grid, to make plotting easier for students:
    # --------------------------------------------------------------------------
    print("interpolating Temperature to regular lon/lat grid for all levels...")
    lon1=np.arange(0.5,360.5,1)
    lat1=np.arange(-89.5,90.5,1)
    points=np.vstack((Temperature_ocean_lon.flatten(),Temperature_ocean_lat.flatten()))
    Temperature_ocean_regular_grid_lon,Temperature_ocean_regular_grid_lat \
        =np.meshgrid(lon1,lat1)
    Ny,Nx=Temperature_ocean_regular_grid_lon.shape
    Nlev=len(Temperature_ocean_lev)
    Temperature_ocean_regular_grid=np.zeros((Nlev,Ny,Nx))
    for i in range(Nlev):
        print("depth = %7.1f" % Temperature_ocean_lev[i])
        if n==0:
            values=Temperature_ocean[0,i,:,:].flatten()
        else:
            values=Temperature_ocean[-1,i,:,:].flatten()
            
        Temperature_ocean_regular_grid[i,:,:]=scipy.interpolate.griddata(points.T,values
                ,(Temperature_ocean_regular_grid_lon,Temperature_ocean_regular_grid_lat)
                ,method='linear')

    Temperature_ocean=1.0*Temperature_ocean_regular_grid
    print("    done.")

    
    if n==0:
        # start year of historical run
        # (there is actually only one time frame in the thetao data,
        # but need to remove the time dimension, hence the following
        # indexing)
        Temperature_ocean_1850=1.0*Temperature_ocean # [0,:,:,:]
    else:
        # last year of rcp8.5 run:
        # (there is actually only one time frame in the thetao data,
        # but need to remove the time dimension, hence the following
        # indexing)
        Temperature_ocean_2100=1.0*Temperature_ocean # [-1,:,:,:]
    
    if n==0:
        sealevel_historical_years=1.0*sealevel_years[[0,-1]]
        sealevel_historical=1.0*sealevel_regular_grid[[0,-1],:,:]
    else:
        sealevel_rcp85_years=1.0*sealevel_years[[0,-1]]
        sealevel_rcp85=1.0*sealevel_regular_grid[[0,-1],:,:]
        
    sealevel_lon=1.0*sealevel_regular_grid_lon
    sealevel_lat=1.0*sealevel_regular_grid_lat
    Temperature_ocean_lon=1.0*Temperature_ocean_regular_grid_lon
    Temperature_ocean_lat=1.0*Temperature_ocean_regular_grid_lat
    
# --------------------------------
# global mean sea level variables:
# --------------------------------
Data_dir="../../../Data-for-teaching-staff/Sea-level/"
ncfile=nc(Data_dir+"zostoga_Omon_CCSM4_historical_r1i1p1_185001-200512.nc",'r')
GMSL_thermosteric_historical=np.asarray(ncfile.variables['zostoga'][:])
GMSL_thermosteric_historical_years=np.asarray(ncfile.variables['time'][:])/365

ncfile=nc(Data_dir+"zostoga_Omon_CCSM4_rcp85_r1i1p1_200501-210012.nc",'r')
GMSL_thermosteric_rcp85=np.asarray(ncfile.variables['zostoga'][:])
GMSL_thermosteric_rcp85_years=np.asarray(ncfile.variables['time'][:])/365

# save variables to be pickled:
np.save("Output/to-pickle/sealevel_historical_years.npy",sealevel_historical_years)
np.save("Output/to-pickle/sealevel_historical.npy",sealevel_historical)
np.save("Output/to-pickle/sealevel_rcp85_years.npy",sealevel_rcp85_years)
np.save("Output/to-pickle/sealevel_rcp85.npy",sealevel_rcp85)
np.save("Output/to-pickle/sealevel_lon.npy",sealevel_lon)
np.save("Output/to-pickle/sealevel_lat.npy",sealevel_lat)
np.save("Output/to-pickle/Temperature_ocean_lev.npy",Temperature_ocean_lev)
np.save("Output/to-pickle/Temperature_ocean_lon.npy",Temperature_ocean_lon)
np.save("Output/to-pickle/Temperature_ocean_lat.npy",Temperature_ocean_lat)
np.save("Output/to-pickle/GMSL_thermosteric_historical.npy",GMSL_thermosteric_historical)
np.save("Output/to-pickle/GMSL_thermosteric_historical_years.npy",GMSL_thermosteric_historical_years)
np.save("Output/to-pickle/GMSL_thermosteric_rcp85.npy",GMSL_thermosteric_rcp85)
np.save("Output/to-pickle/GMSL_thermosteric_rcp85_years.npy",GMSL_thermosteric_rcp85_years)
np.save("Output/to-pickle/Temperature_ocean_1850.npy",Temperature_ocean_1850)
np.save("Output/to-pickle/Temperature_ocean_2100.npy",Temperature_ocean_2100)
np.save("Output/to-pickle/areacello.npy",areacello)
