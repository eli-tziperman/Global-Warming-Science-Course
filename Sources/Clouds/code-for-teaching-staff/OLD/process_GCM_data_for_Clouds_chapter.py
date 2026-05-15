"""
calculate
Delta_T
Delta_CRF_SW
Delta_CRF_LW
cloud_TOT
for HadGEM2-ES and GFDL-ESM2G models,
where Delta=RCP8.5 @ 2100 - historical @ 1850.
CMIP variable names used for this:
clt
lat
lon
rlds
rldscs
rsds
rsdscs
tas
"""
import numpy as np
import pickle
import os
from netCDF4 import Dataset

data_dir='/Users/eli/Dropbox/Courses/EPS101/Data-for-teaching-staff/Clouds/'


# Calculate change in CRF, both LW and SW, from historical to RCP8.5:
# -------------------------------------------------------------------

# clouds:
file=data_dir+'CLT_GFDL_historical.nc';     nc1=Dataset(file, 'r');
file=data_dir+'CLT_GFDL_rcp85.nc';          nc2=Dataset(file, 'r');
file=data_dir+'CLT_Hadley_historical.nc';   nc3=Dataset(file, 'r');
file=data_dir+'CLT_Hadley_rcp85.nc';        nc4=Dataset(file, 'r');

clouds_GFDL_historical  =np.asarray(nc1.variables['clt'][:])
clouds_GFDL_rcp85       =np.asarray(nc2.variables['clt'][:])
clouds_Hadley_historical=np.asarray(nc3.variables['clt'][:])
clouds_Hadley_rcp85     =np.asarray(nc4.variables['clt'][:])
clouds_Hadley_longitude =np.asarray(nc3.variables['lon'][:])
clouds_Hadley_latitude  =np.asarray(nc3.variables['lat'][:])
clouds_GFDL_longitude   =np.asarray(nc1.variables['lon'][:])
clouds_GFDL_latitude    =np.asarray(nc1.variables['lat'][:])

# Delta_LW_CRF_GFDL
file=data_dir+'LW_GFDL_historical.nc';     nc1=Dataset(file, 'r');
file=data_dir+'LWcs_GFDL_historical.nc';   nc2=Dataset(file, 'r');
file=data_dir+'LW_GFDL_rcp85.nc';          nc3=Dataset(file, 'r');
file=data_dir+'LWcs_GFDL_rcp85.nc';        nc4=Dataset(file, 'r');

Delta_LW_CRF_GFDL=np.asarray((nc3.variables['rlds'][:]-nc4.variables['rldscs'][:]) \
                             -(nc1.variables['rlds'][:]-nc2.variables['rldscs'][:]))

# Delta_LW_CRF_Hadley
file=data_dir+'LW_Hadley_historical.nc';   nc1=Dataset(file, 'r');
file=data_dir+'LWcs_Hadley_historical.nc'; nc2=Dataset(file, 'r');
file=data_dir+'LW_Hadley_rcp85.nc';        nc3=Dataset(file, 'r');
file=data_dir+'LWcs_Hadley_rcp85.nc';      nc4=Dataset(file, 'r');

Delta_LW_CRF_Hadley=np.asarray((nc3.variables['rlds'][:]-nc4.variables['rldscs'][:]) \
                               -(nc1.variables['rlds'][:]-nc2.variables['rldscs'][:]))

# Delta_SW_CRF_GFDL
file=data_dir+'SW_GFDL_historical.nc';     nc1=Dataset(file, 'r');
file=data_dir+'SWcs_GFDL_historical.nc';   nc2=Dataset(file, 'r');
file=data_dir+'SW_GFDL_rcp85.nc';          nc3=Dataset(file, 'r');
file=data_dir+'SWcs_GFDL_rcp85.nc';        nc4=Dataset(file, 'r');

Delta_SW_CRF_GFDL=np.asarray((nc3.variables['rsds'][:]-nc4.variables['rsdscs'][:]) \
                             -(nc1.variables['rsds'][:]-nc2.variables['rsdscs'][:]))

# Delta_SW_CRF_Hadley
file=data_dir+'SW_Hadley_historical.nc';   nc1=Dataset(file, 'r');
file=data_dir+'SWcs_Hadley_historical.nc'; nc2=Dataset(file, 'r');
file=data_dir+'SW_Hadley_rcp85.nc';        nc3=Dataset(file, 'r');
file=data_dir+'SWcs_Hadley_rcp85.nc';      nc4=Dataset(file, 'r');

Delta_SW_CRF_Hadley=np.asarray((nc3.variables['rsds'][:]-nc4.variables['rsdscs'][:]) \
                               -(nc1.variables['rsds'][:]-nc2.variables['rsdscs'][:]))

# Calculate change in SAT from historical to RCP8.5:
# --------------------------------------------------

# Delta_SAT_GFDL:
file=data_dir+'SAT_GFDL_historical.nc'; nc1=Dataset(file, 'r');
file=data_dir+'SAT_GFDL_rcp85.nc';      nc2=Dataset(file, 'r');

Delta_SAT_GFDL=np.asarray((nc2.variables['tas'][:]-nc1.variables['tas'][:]))

# Delta_SAT_Hadley:
file=data_dir+'SAT_Hadley_historical.nc'; nc1=Dataset(file, 'r');
file=data_dir+'SAT_Hadley_rcp85.nc';      nc2=Dataset(file, 'r');

Delta_SAT_Hadley=np.asarray((nc2.variables['tas'][:]-nc1.variables['tas'][:]))

# save data to be pickled:
# ------------------------
np.save("Output/to-pickle/Delta_LW_CRF_GFDL.npy",Delta_LW_CRF_GFDL[0,:,:])
np.save("Output/to-pickle/Delta_LW_CRF_Hadley.npy",Delta_LW_CRF_Hadley[0,:,:])
np.save("Output/to-pickle/Delta_SW_CRF_GFDL.npy",Delta_SW_CRF_GFDL[0,:,:])
np.save("Output/to-pickle/Delta_SW_CRF_Hadley.npy",Delta_SW_CRF_Hadley[0,:,:])
np.save("Output/to-pickle/Delta_SAT_GFDL.npy",Delta_SAT_GFDL[0,:,:])
np.save("Output/to-pickle/Delta_SAT_Hadley.npy",Delta_SAT_Hadley[0,:,:])
np.save("Output/to-pickle/clouds_GFDL_historical.npy",clouds_GFDL_historical[0,:,:])
np.save("Output/to-pickle/clouds_GFDL_rcp85.npy",clouds_GFDL_rcp85[0,:,:])
np.save("Output/to-pickle/clouds_Hadley_historical.npy",clouds_Hadley_historical[0,:,:])
np.save("Output/to-pickle/clouds_Hadley_rcp85.npy",clouds_Hadley_rcp85[0,:,:])
np.save("Output/to-pickle/clouds_Hadley_longitude.npy",clouds_Hadley_longitude)
np.save("Output/to-pickle/clouds_Hadley_latitude.npy",clouds_Hadley_latitude)
np.save("Output/to-pickle/clouds_GFDL_longitude.npy",clouds_GFDL_longitude)
np.save("Output/to-pickle/clouds_GFDL_latitude.npy",clouds_GFDL_latitude)

