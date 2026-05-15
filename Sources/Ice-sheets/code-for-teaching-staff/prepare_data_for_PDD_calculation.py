import numpy as np
import pickle
from netCDF4 import Dataset as nc

def pickle_vars(fileName, env, *variables):
    d = dict([(x, env[x]) for v in variables for x in env if v is env[x]])
    with open(fileName, 'wb') as f:
        pickle.dump(d, f)

data_directory='/Users/eli/Dropbox/Courses/EPS101/Data-for-teaching-staff/Ice-sheets/'
# near surface air temperature
filenames=[data_directory+'tas_day_GFDL-ESM2G_piControl_r1i1p1_0499.nc'
           ,data_directory+'tas_day_GFDL-ESM2G_rcp85_r1i1p1_2099.nc']
# downloaded from https://esgf-node.llnl.gov/search/cmip5/

for n in range(len(filenames)):
    filename=filenames[n]
    ncfile=nc(filename,'r')  # open the nc file and read data
    SAT_lon=np.asarray(ncfile.variables['lon'][:])
    SAT_lat=np.asarray(ncfile.variables['lat'][:])
    SAT_time=np.asarray(ncfile.variables['time'][:])
    if n==0:
        SAT_control=np.asarray(ncfile.variables['tas'][:])
    else:
        SAT_rcp85=np.asarray(ncfile.variables['tas'][:])


# land ice coverage mask
filenames=[data_directory+'sftgif_fx_GFDL-ESM2G_esmControl_r0i0p0.nc'\
           ,data_directory+'sftgif_fx_GFDL-ESM2G_esmrcp85_r0i0p0.nc']
# downloaded from https://esgf-node.llnl.gov/search/cmip5/

for n in range(len(filenames)):
    filename=filenames[n]
    ncfile=nc(filename,'r')  # open the nc file and read data
    landice_lon=np.asarray(ncfile.variables['lon'][:])
    landice_lat=np.asarray(ncfile.variables['lat'][:])
    if n==0:
        lons, lats = np.meshgrid(landice_lon, landice_lat)
        landice_greenland_mask_control=np.asarray( \
                                    ((ncfile.variables['sftgif'][:]>0.1) \
                                   & (lats>60) & (lons<340) & (lons>286) \
                                   & (lats+lons/1.5>268))\
                                   )
        landice_antarctica_mask_control=np.asarray( \
                                    ((ncfile.variables['sftgif'][:]>0.1) \
                                    & (lats<-60))\
                                   )
    else:
        landice_greenland_mask_rcp85=np.asarray( \
                                    ((ncfile.variables['sftgif'][:]>0.1) \
                                 & (lats>60) & (lons<340) & (lons>286) \
                                 & (lats+lons/1.5>268))\
                                   )
        landice_antarctica_mask_rcp85=np.asarray( \
                                    ((ncfile.variables['sftgif'][:]>0.1) \
                                  & (lats<-60))\
                                   )

# save for pickling:
np.save("Output/to-pickle/landice_lon",landice_lon)
np.save("Output/to-pickle/landice_lat.npy",landice_lat)
np.save("Output/to-pickle/landice_greenland_mask_control.npy",landice_greenland_mask_control)
np.save("Output/to-pickle/landice_antarctica_mask_control.npy",landice_antarctica_mask_control)
np.save("Output/to-pickle/landice_greenland_mask_rcp85.npy",landice_greenland_mask_rcp85)
np.save("Output/to-pickle/landice_antarctica_mask_rcp85.npy",landice_antarctica_mask_rcp85)
np.save("Output/to-pickle/SAT_control.npy",SAT_control)
np.save("Output/to-pickle/SAT_rcp85.npy",SAT_rcp85)
np.save("Output/to-pickle/SAT_lon",SAT_lon)
np.save("Output/to-pickle/SAT_lat.npy",SAT_lat)
np.save("Output/to-pickle/SAT_time.npy",SAT_time)
