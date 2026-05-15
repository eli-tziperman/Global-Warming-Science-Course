#!/bin/bash
export CDIR="../../../EPS101-Cheyenne/Output"
/bin/cp -pf $CDIR/AIS_net_SMB_map.npy $CDIR/AIS_net_SMB_map_lat.npy \
   $CDIR/AIS_net_SMB_map_lon.npy \
   $CDIR/AIS_net_SMB_timeseries_annual_avg.npy \
   $CDIR/AIS_net_SMB_timeseries_annual_std.npy \
   $CDIR/AIS_evap_timeseries_annual_avg.npy \
   $CDIR/AIS_evap_timeseries_annual_std.npy \
   $CDIR/GIS_net_SMB_map.npy \
   $CDIR/GIS_net_SMB_map_lat.npy $CDIR/GIS_net_SMB_map_lon.npy \
   $CDIR/GIS_net_SMB_timeseries_annual_avg.npy \
   $CDIR/GIS_net_SMB_timeseries_annual_std.npy \
   $CDIR/GIS_evap_timeseries_annual_avg.npy \
   $CDIR/GIS_evap_timeseries_annual_std.npy \
   $CDIR/SMB_timeseries_annual_years.npy \
   ./Output/to-pickle/

python prepare_data_for_PDD_calculation.py

python pickle_vars_for_students.py
