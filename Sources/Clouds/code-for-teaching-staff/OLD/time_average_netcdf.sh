#!/bin/bash
# time mean using NCO operators:
# ncra -F -d time,1,,1 input_file output_file

data_dir=/Users/eli/Dropbox/Courses/EPS101/Data-for-teaching-staff/Clouds

ncra -F -d time,1,,1 $data_dir/rlds_Amon_GFDL-ESM2G_historical_r1i1p1_186101-186512.nc   $data_dir/LW_GFDL_historical.nc
ncra -F -d time,1,,1 $data_dir/rldscs_Amon_GFDL-ESM2G_historical_r1i1p1_186101-186512.nc $data_dir/LWcs_GFDL_historical.nc
ncra -F -d time,1,,1 $data_dir/rsds_Amon_GFDL-ESM2G_historical_r1i1p1_186101-186512.nc   $data_dir/SW_GFDL_historical.nc
ncra -F -d time,1,,1 $data_dir/rsdscs_Amon_GFDL-ESM2G_historical_r1i1p1_186101-186512.nc $data_dir/SWcs_GFDL_historical.nc
ncra -F -d time,1,,1 $data_dir/tas_Amon_GFDL-ESM2G_historical_r1i1p1_186101-186512.nc    $data_dir/SAT_GFDL_historical.nc
ncra -F -d time,1,,1 $data_dir/clt_Amon_GFDL-ESM2G_historical_r1i1p1_186101-186512.nc    $data_dir/CLT_GFDL_historical.nc

ncra -F -d time,1,,1 $data_dir/rldscs_Amon_GFDL-ESM2G_rcp85_r1i1p1_209601-210012.nc      $data_dir/LWcs_GFDL_rcp85.nc
ncra -F -d time,1,,1 $data_dir/rlds_Amon_GFDL-ESM2G_rcp85_r1i1p1_209601-210012.nc        $data_dir/LW_GFDL_rcp85.nc
ncra -F -d time,1,,1 $data_dir/rsdscs_Amon_GFDL-ESM2G_rcp85_r1i1p1_209601-210012.nc      $data_dir/SWcs_GFDL_rcp85.nc
ncra -F -d time,1,,1 $data_dir/rsds_Amon_GFDL-ESM2G_rcp85_r1i1p1_209601-210012.nc        $data_dir/SW_GFDL_rcp85.nc
ncra -F -d time,1,,1 $data_dir/tas_Amon_GFDL-ESM2G_rcp85_r1i1p1_209601-210012.nc         $data_dir/SAT_GFDL_rcp85.nc
ncra -F -d time,1,,1 $data_dir/clt_Amon_GFDL-ESM2G_rcp85_r1i1p1_209601-210012.nc         $data_dir/CLT_GFDL_rcp85.nc

ncra -F -d time,1,,1 $data_dir/rsdscs_Amon_HadGEM2-ES_historical_r4i1p1_185912-188411.nc $data_dir/SWcs_Hadley_historical.nc
ncra -F -d time,1,,1 $data_dir/rsds_Amon_HadGEM2-ES_historical_r4i1p1_185912-188411.nc   $data_dir/SW_Hadley_historical.nc
ncra -F -d time,1,,1 $data_dir/rldscs_Amon_HadGEM2-ES_historical_r4i1p1_185912-188411.nc $data_dir/LWcs_Hadley_historical.nc
ncra -F -d time,1,,1 $data_dir/rlds_Amon_HadGEM2-ES_historical_r4i1p1_185912-188411.nc   $data_dir/LW_Hadley_historical.nc
ncra -F -d time,1,,1 $data_dir/tas_Amon_HadGEM2-ES_historical_r4i1p1_185912-188411.nc    $data_dir/SAT_Hadley_historical.nc
ncra -F -d time,1,,1 $data_dir/clt_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc    $data_dir/CLT_Hadley_historical.nc

ncra -F -d time,1,,1 $data_dir/rsdscs_Amon_HadGEM2-ES_rcp85_r1i1p1_208012-209912.nc      $data_dir/SWcs_Hadley_rcp85.nc
ncra -F -d time,1,,1 $data_dir/rsds_Amon_HadGEM2-ES_rcp85_r1i1p1_208012-209912.nc        $data_dir/SW_Hadley_rcp85.nc
ncra -F -d time,1,,1 $data_dir/rldscs_Amon_HadGEM2-ES_rcp85_r1i1p1_208012-209912.nc      $data_dir/LWcs_Hadley_rcp85.nc
ncra -F -d time,1,,1 $data_dir/rlds_Amon_HadGEM2-ES_rcp85_r1i1p1_208012-209912.nc        $data_dir/LW_Hadley_rcp85.nc
ncra -F -d time,1,,1 $data_dir/tas_Amon_HadGEM2-ES_rcp85_r1i1p1_208012-209912.nc         $data_dir/SAT_Hadley_rcp85.nc
ncra -F -d time,1,,1 $data_dir/clt_Amon_HadGEM2-ES_rcp85_r1i1p1_208012-209912.nc         $data_dir/CLT_Hadley_rcp85.nc

