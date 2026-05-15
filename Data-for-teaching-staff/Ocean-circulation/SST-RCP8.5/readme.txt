Downloaded SST for first and last 5 year periods of RCP8.5 (2006-2010, and 2095-100) from
https://esgf-node.llnl.gov/search/cmip5/

Used NCO to time-average each:
ncwa -xC -v time -a time tos_Omon_GFDL-ESM2M_rcp85_r1i1p1_200601-201012.nc tos_Omon_GFDL-ESM2M_rcp85_r1i1p1_200601-201012-avg.nc

ncwa -xC -v time -a time tos_Omon_GFDL-ESM2M_rcp85_r1i1p1_209601-210012.nc tos_Omon_GFDL-ESM2M_rcp85_r1i1p1_209601-210012-avg.nc
