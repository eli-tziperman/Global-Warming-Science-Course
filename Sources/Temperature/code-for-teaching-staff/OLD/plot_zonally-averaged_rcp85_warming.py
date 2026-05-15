import numpy as np
from numpy import linalg
import scipy as scipy
import matplotlib.pyplot as plt
import matplotlib
from netCDF4 import Dataset

filename='/Users/eli/Courses/EPS101/Data-for-teaching-staff/Temperature/ta_RCP85_gfdl/ta_Amon_GFDL-CM3_RCP85_r1i1p1_200601-201012-txavg.nc';
ncfile = Dataset(filename, 'r');

file2='/Users/eli/Courses/EPS101/Data-for-teaching-staff/Temperature/ta_RCP85_gfdl/ta_Amon_GFDL-CM3_RCP85_r1i1p1_209601-210012-txavg.nc'
ncfile2 = Dataset(file2, 'r');

TA1 = np.asarray(ncfile.variables['ta'][:]);
TA2 = np.asarray(ncfile2.variables['ta'][:]);
plev=np.asarray(ncfile.variables['plev'][:]);
lat=np.asarray(ncfile.variables['lat'][:]);
R=287      # gas constant J/kg/K\n",
g=9.8
Tbar=260
height=-np.log(plev/100000)*R*Tbar/g/1000

# calculate warming as func of latitude and height:
TA1[TA1>1.e5]=np.nan
TA2[TA2>1.e5]=np.nan
RCP85_zonally_avg_T_2010=TA1[0,:,:];
RCP85_zonally_avg_T_2100=TA2[0,:,:]
RCP85_zonally_avg_T_lat=lat
RCP85_zonally_avg_T_height=height
np.save("Output/to-pickle/RCP85_zonally_avg_T_2010.npy"
        ,RCP85_zonally_avg_T_2010)
np.save("Output/to-pickle/RCP85_zonally_avg_T_2100.npy"
        ,RCP85_zonally_avg_T_2100)
np.save("Output/to-pickle/RCP85_zonally_avg_T_lat.npy"
        ,RCP85_zonally_avg_T_lat)
np.save("Output/to-pickle/RCP85_zonally_avg_T_height.npy"
        ,RCP85_zonally_avg_T_height)


# calculate averaged vertical profile in midlatitudes:
RCP85_zonally_avg_warming=RCP85_zonally_avg_T_2100-RCP85_zonally_avg_T_2010
TA1_midlats=RCP85_zonally_avg_T_2010[:,np.logical_and(lat>30,lat<50)]
TA2_midlats=RCP85_zonally_avg_T_2100[:,np.logical_and(lat>30,lat<50)]
TA1_midlats_avg=np.nanmean(TA1_midlats,1)
TA2_midlats_avg=np.nanmean(TA2_midlats,1)

fig=plt.figure(figsize=(7,3),dpi=200)
plt.clf()
props = dict(boxstyle='round', edgecolor="wheat", facecolor='wheat', alpha=0.9)

# plot 
plt.subplot(1,2,1)
plt.plot(TA1_midlats_avg,height,color="b",label="2006-2010")
plt.plot(TA2_midlats_avg,height,color="r",label="2096-2100")
plt.xlabel('Temperature (K)')
plt.ylim([0,50])
#plt.ylabel('height (km)')
plt.legend()
ax=plt.gca()
ax.text(0.06, 0.93, "(a)", transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)

plt.subplot(1,2,2)
# plot latitude-hjeight section of warming:
levels=np.arange(-16,17,1)
plt.contourf(lat,height,RCP85_zonally_avg_warming,levels)
#plt.gca().invert_yaxis()
plt.set_cmap('bwr')
hcb=plt.colorbar()
hcb.set_label("$^\\circ$C")
plt.xlabel('Latitude')
plt.ylabel('height (km)')
plt.ylim([0,50])
plt.xticks(range(-90,120,30))
ax=plt.gca()
ax.text(0.06, 0.93, "(b)", transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)

plt.tight_layout()
fig.savefig("Output/Figures/temperature-zonally-averaged-warming-RCP85-GFDL.pdf")
plt.show()
