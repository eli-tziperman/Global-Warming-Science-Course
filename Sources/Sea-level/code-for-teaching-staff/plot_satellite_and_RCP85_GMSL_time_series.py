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

print("Satellite: using columns (0 is first) 2,8: year and GMSL (Global Isostatic Adjustment (GIA) applied) variation (mm) ")
years=data[:,2]
GMSL=data[:,8]

# Import RCP8.5 csv datasets:
# ---------------------------
folder='../../../Data-for-teaching-staff/Sea-level/IPCC-sea-level-Fig-13.11a-RCP85/'
dataset = pd.read_csv(folder+'red.csv',header=None)
red = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'black.csv',header=None)
black = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'green.csv',header=None)
green = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'cyan.csv',header=None)
cyan = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'blue.csv',header=None)
blue = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'dash_blue.csv',header=None)
dash_blue = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'dash_green.csv',header=None)
dash_green = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'dash_purple.csv',header=None)
dash_purple = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'grey_lower.csv',header=None)
grey_lower = np.asarray(dataset.iloc[:, :].values)

dataset = pd.read_csv(folder+'grey_upper.csv',header=None)
grey_upper = np.asarray(dataset.iloc[:, :].values)

# interpolate two grey curve to same x-values so that they can be used
# to plot a filled error range:
grey_upper_interp = np.interp(grey_lower[:,0], grey_upper[:,0], grey_upper[:,1])


fig=plt.figure(figsize=(6,2.5),dpi=200)

# --------------------
# plot satellite GMSL:
# --------------------
plt.subplot(1,2,1)
plt.plot(years,GMSL,lw=1,color="r",label="area burnt")
#plt.xlim([1983,2016])
ax=plt.gca();
plt.xlabel("Year")
plt.ylabel("GMSL (mm)")
plt.grid(lw=0.25)
plt.title("(a)",loc="left")

# --------------------
# plot RCP5.5 GMSL:
# --------------------
plt.subplot(1,2,2)
plt.fill_between(grey_lower[:,0],grey_lower[:,1],grey_upper_interp,lw=0.1,color="grey")
plt.plot(black[:,0],black[:,1],"-",lw=1,color="k",label="Sum")
plt.plot(red[:,0],red[:,1],"-",lw=1,color="r",label="Thermal expansion")
plt.plot(cyan[:,0],cyan[:,1],"-",lw=1,color="c",label="Glaciers")
plt.plot(green[:,0],green[:,1],"-",lw=1,color="g",label="Greenland")
plt.plot(dash_blue[:,0],dash_blue[:,1],"--",lw=1,color="b",label="Antarctic rapid dyn")
plt.plot(dash_green[:,0],dash_green[:,1],"--",lw=1,color="g",label="Greenland rapid dyn")
plt.plot(dash_purple[:,0],dash_purple[:,1],"--",lw=1,color="purple",label="Land water storage")
plt.plot(blue[:,0],blue[:,1],"-",lw=1,color="b",label="Antarctic")
plt.xlim([2005,2100])
plt.ylim([0,1])
ax=plt.gca();
plt.xlabel("Year")
plt.ylabel("GMSL (m)")
plt.grid(lw=0.25)
plt.title("(b)",loc="left")
plt.legend(fontsize=6,frameon=False,loc=(0.02,0.28))

# finalize plot:
plt.tight_layout()
fig.savefig("Output/sea-level-satellite_obs_and_RCP85.pdf"
            ,bbox_inches='tight',pad_inches = 0)
plt.show()
