1) download CMIP5 data: https://esgf-node.llnl.gov/search/cmip5/

Need to download cloud data (lon/lat of low and high clouds, total CRF, for RCP8.5 year 2100 and present-day, each averaged over a decade or so) for two models. Also surface air temperature for both models for same periods, to demonstrate the different climate sensitivities.

Specifically, given CMIP5 variable conventions:	short-name
downwelling longwave radiation:			rlds
downwelling clear-sky longwave radiation:	rldscs
downwelling shortwave radiation:		rsds
downwelling clear-sky shortwave radiation:	rsdscs
near-surface air temperature:			tas
total cloud fraction:				clt

Search Constraints:   atmos | Downwelling Clear-Sky Longwave Radiation,Downwelling Clear-Sky Shortwave Radiation,Downwelling Longwave Radiation,Downwelling Shortwave Radiation,Near-Surface Air Temperature | CMIP5 | GFDL-ESM2G,HadGEM2-ES | historical,rcp85 | mon

Looking at the paper:

"Forcing, feedbacks and climate sensitivity in CMIP5 coupled atmosphere-ocean climate models" by Timothy Andrews, Jonathan M. Gregory, Mark J. Webb, and Karl E. Taylor,

Based on Table 1 and Figure 2, it seems that two good models, that are from reliable sources but show very different climate sensitivity are:

HadGEM2-ES
GFDL-ESM2G

Once downloaded, move to the data directory
~/Dropbox/Courses/EPS101/Data-for-teaching-staff/Clouds

2) time-mean:
 using the script time_average_netcdf.sh

3) calculate CRF and pickle for students:
using 
