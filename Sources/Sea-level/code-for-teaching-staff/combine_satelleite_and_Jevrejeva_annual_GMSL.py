import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from scipy.stats import linregress

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

# Import satellite csv dataset:
# -----------------------------
dataset = pd.read_csv('../../../Data-for-teaching-staff/Sea-level/satellite-record/GMSL_TPJAOS_5.2.txt',sep=r'\s+',comment='H')
data = np.asarray(dataset.iloc[:, :].values)
# data columns to use (need to shift by one as python starts at 0):
# HDR 3 year+fraction of year (mid-cycle) 
# HDR 9 GMSL (Global Isostatic Adjustment (GIA applied) variation (mm)
#     with respect to 20-year TOPEX/Jason collinear mean reference
# HDR 10 standard deviation of GMSL (GIA applied) variation estimate (mm)
GMSL_satellite_years=data[:,2]
GMSL_satellite=data[:,8]
GMSL_satellite_error=data[:,9]

# Import Jevrejeva csv dataset:
# -----------------------------
data=np.asarray(pd.read_table("../../../Data-for-teaching-staff/Sea-level/Jevrejeva_etal_2008.txt",skiprows=14,sep=r'\s+'))

GMSL_Jevrejeva_years=data[:,0]
GMSL_Jevrejeva=data[:,1]
GMSL_Jevrejeva_error=data[:,2]


# calculate annual mean satellite record:
# ---------------------------------------
min_satellite_year=int(min(GMSL_satellite_years))
max_satellite_year=2019
GMSL_satellite_annual_mean_years=np.arange(min_satellite_year,max_satellite_year)
GMSL_satellite_annual_mean=0.0*GMSL_satellite_annual_mean_years
GMSL_satellite_annual_mean_error=0.0*GMSL_satellite_annual_mean_years
iyear=-1
for year in GMSL_satellite_annual_mean_years:
    iyear=iyear+1
    # add an offset to match Jevrejeva record
    offset=156
    GMSL_satellite_annual_mean[iyear] \
       =np.mean(GMSL_satellite[np.floor(GMSL_satellite_years)==year])+offset
    GMSL_satellite_annual_mean_error[iyear] \
       =np.mean(GMSL_satellite_error[np.floor(GMSL_satellite_years)==year])

# save annyal-mean GMSL data sets with error bars to be plotted for
# introduction chapter:
np.save("Output/for-introduction/GMSL_Jevrejeva_years.npy",GMSL_Jevrejeva_years)
np.save("Output/for-introduction/GMSL_Jevrejeva.npy",GMSL_Jevrejeva)
np.save("Output/for-introduction/GMSL_Jevrejeva_error.npy",GMSL_Jevrejeva_error)
np.save("Output/for-introduction/GMSL_satellite_years.npy",GMSL_satellite_annual_mean_years)
np.save("Output/for-introduction/GMSL_satellite.npy",GMSL_satellite_annual_mean)
np.save("Output/for-introduction/GMSL_satellite_error.npy",GMSL_satellite_annual_mean_error)


# CRUDELY combine two data sets:
GMSL_combined=np.hstack(( \
    GMSL_Jevrejeva[GMSL_Jevrejeva_years<2000]\
    ,GMSL_satellite_annual_mean[GMSL_satellite_annual_mean_years>=2000]))
GMSL_combined_years=np.hstack(( \
    GMSL_Jevrejeva_years[GMSL_Jevrejeva_years<2000]\
    ,GMSL_satellite_annual_mean_years[GMSL_satellite_annual_mean_years>=2000]))

# save combined data for students:
np.save("Output/to-pickle/GMSL_since_1700_years.npy",GMSL_combined_years)
np.save("Output/to-pickle/GMSL_since_1700.npy",GMSL_combined)

    
# ------------------------------------------
# plot both records for finding best offset:
# ------------------------------------------
fig=plt.figure(figsize=(5,4),dpi=170)
plt.plot(GMSL_satellite_annual_mean_years,GMSL_satellite_annual_mean,lw=1,color="r",label="satellite")
plt.plot(GMSL_Jevrejeva_years,GMSL_Jevrejeva,lw=1,color="c",label="Jevrejeva")
plt.plot(GMSL_combined_years,GMSL_combined,lw=0.5,color="k",label="combined")
#plt.xlim([1983,2016])
ax=plt.gca();
plt.xlabel("year")
plt.ylabel("GMSL (mm)")
plt.grid(lw=0.25)
ax=plt.gca()

# finalize plot:
plt.tight_layout()
plt.show()


# -------------------------------------------------
# plot both records with errors for chapter figure:
# -------------------------------------------------
fig=plt.figure(figsize=(5,4),dpi=170)
# Jevrejeva_etal_2008
GMSL_Jevrejeva=np.load("../../Sea-level/code-for-teaching-staff/Output/for-introduction/GMSL_Jevrejeva.npy")/10
GMSL_Jevrejeva_error=np.load("../../Sea-level/code-for-teaching-staff/Output/for-introduction/GMSL_Jevrejeva_error.npy")/10
GMSL_Jevrejeva_years=np.load("../../Sea-level/code-for-teaching-staff/Output/for-introduction/GMSL_Jevrejeva_years.npy")
plt.plot(GMSL_Jevrejeva_years,GMSL_Jevrejeva,color=[0,0,1],lw=1)
plt.fill_between(GMSL_Jevrejeva_years,GMSL_Jevrejeva-GMSL_Jevrejeva_error \
                 ,GMSL_Jevrejeva+GMSL_Jevrejeva_error,lw=0.1,color=[0,0.75,1])

#satellite:
GMSL_satellite=np.load("../../Sea-level/code-for-teaching-staff/Output/for-introduction/GMSL_satellite.npy")/10
GMSL_satellite_error=np.load("../../Sea-level/code-for-teaching-staff/Output/for-introduction/GMSL_satellite_error.npy")/100
GMSL_satellite_years=np.load("../../Sea-level/code-for-teaching-staff/Output/for-introduction/GMSL_satellite_years.npy")
plt.plot(GMSL_satellite_years,GMSL_satellite,color=[1,0,0],lw=1)
plt.fill_between(GMSL_satellite_years,GMSL_satellite-GMSL_satellite_error\
                 ,GMSL_satellite+GMSL_satellite_error,lw=0.1,color=[1,0.75,0])

plt.xlabel('Year')
plt.ylabel('GMSL (cm)')
plt.xlim(1700,2025)
plt.ylim(-30,23)
#ax1=plt.gca()
#ax1.yaxis.set_ticks_position("right")
#ax1.yaxis.set_label_position("right")
plt.grid(lw=0.25)
#ax1.text(0.04, 0.93, "(d)", transform=ax1.transAxes, fontsize=12,
#        verticalalignment='top', bbox=props)
# finalize plot:
plt.tight_layout()
fig.savefig("Output/sea-level-combined_Jevrejeva_etal_2008_satellite.pdf"
            ,bbox_inches='tight',pad_inches = 0)
plt.show()
