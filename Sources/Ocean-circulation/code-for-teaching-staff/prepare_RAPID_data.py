import numpy as np
from numpy import linalg
import scipy as scipy
import matplotlib.pyplot as plt
import matplotlib
from netCDF4 import Dataset
from scipy.optimize import fmin
import datetime
import pandas as pd

def sine_fit_cost(x):
    # function to be minimized to calculate sine fit
    RAPID_AMOC_sine_fit=x[0]+x[1]*np.sin(2*np.pi*(RAPID_time_smooth+x[2])/365)
    square_diff= np.power(np.subtract(RAPID_AMOC_sine_fit, RAPID_AMOC_data_smooth),2)
    cost=np.sum(square_diff)
    return cost


# read data:
# ----------
filename='../../../Data-for-teaching-staff/Ocean-circulation/RAPID/RAPID_moc_transports.nc';
ncfile = Dataset(filename, 'r');
RAPID_AMOC_data = np.array(ncfile.variables['moc_mar_hc10'][:])
RAPID_time = np.array(ncfile.variables['time'][:])


# use only unmasked data values and smooth data:
# ----------------------------------------------
RAPID_time = RAPID_time[RAPID_AMOC_data>-1000.0]
RAPID_AMOC_data = RAPID_AMOC_data[RAPID_AMOC_data>-1000.0]


# get an array of dates for the time axis:
# ----------------------------------------
# time:units = "days since 2004-4-1 00:00:00"
# translate time to days since 2004-01-01:
RAPID_time=RAPID_time+91.
# get an array of dates for the time axis
dates=[]
for i in range(0,len(RAPID_time)):
    dates.append(datetime.datetime(2004, 1, 1) + datetime.timedelta(RAPID_time[i] - 1))

    
# smooth data:
# ------------
N=59 # use an odd number
RAPID_AMOC_data_smooth = np.convolve(RAPID_AMOC_data, np.ones((N,))/N, mode='valid')
RAPID_time_smooth=RAPID_time[int(np.floor(N/2)):-int(np.floor(N/2))]
RAPID_dates_smooth=dates[int(np.floor(N/2)):-int(np.floor(N/2))]
#print(RAPID_AMOC_data_smooth.shape[0])
#print(int(RAPID_time_smooth.shape[0]))


# get Bryden data:
# ----------------
#              1957  1981  1992  1998  2004
#               Oct   Sep   Aug   Feb   May
#              +22.9 +18.7 +19.4 +16.1 +14.8
Bryden_months=np.array([10,9,8,2,5])+0.5
Bryden_AMOC=np.array([+22.9,+18.7,+19.4,+16.1,+14.8])
Bryden_years=[1957,  1981,  1992,  1998,  2004]

# fit a seasonal cycle to the AMOC data:
# --------------------------------------
x0 = [17,3,-90]
RAPID_sine_fit_coeffs = fmin(sine_fit_cost, x0, disp=False)
#print("fmin solution: RAPID_sine_fit_coeffs=",RAPID_sine_fit_coeffs)
a=1.0*RAPID_sine_fit_coeffs
RAPID_AMOC_sine_fit=a[0]+a[1]*np.sin(2*np.pi*(RAPID_time+a[2])/365)

# calculate RAPID monthly climatology:
# ------------------------------------
df = pd.DataFrame({'dates': RAPID_dates_smooth, 'AMOC': RAPID_AMOC_data_smooth})
df = df.set_index('dates')
df['Month'] = df.index.month
RAPID_AMOC_monthly_climatology = df.groupby('Month').mean()
#print(RAPID_AMOC_monthly_climatology)


# plot AMOC monthly climatology with Bryden data superimposed:
# ------------------------------------------------------------
fig=plt.figure(figsize=(12,6))
plt.subplot(1,2,1)
time_months=(0.5+np.arange(1,13))
time_sine_fit_months=np.arange(0,12,0.1)
plt.plot(time_months,RAPID_AMOC_monthly_climatology,'rx'\
         ,markersize=15,label="RAPID monthly climatology")
Y=a[0]+a[1]*np.sin(2*np.pi*(time_sine_fit_months*(365/12)+a[2])/365)
plt.plot(time_sine_fit_months,Y,label="sine fit")
X=Bryden_months[:]
Y=Bryden_AMOC[:]
plt.scatter(X,Y,label="AMOC ship obs")
for i in range(len(X)):
    plt.text(X[i],Y[i],str(Bryden_years[i]))
plt.xlabel("time (months)")
plt.ylabel("Sv")
plt.xlim(0,12)
plt.legend()


# plot AMOC time series with sine fit:
# ------------------------------------
plt.subplot(1,2,2)
plt.plot(RAPID_dates_smooth,RAPID_AMOC_data_smooth,label="RAPID obs, smoothed")
Y=RAPID_AMOC_sine_fit[int(np.floor(N/2)):-int(np.floor(N/2))]
plt.plot(RAPID_dates_smooth,Y,label="sine fit")
plt.xlabel("Time")
plt.ylabel("Sv")
plt.legend()

plt.tight_layout()
plt.show()



# save data for students:
# -----------------------
np.save("Output/to-pickle/ship_obs_months.npy",Bryden_months)
np.save("Output/to-pickle/ship_obs_AMOC.npy",Bryden_AMOC)
np.save("Output/to-pickle/ship_obs_years.npy",Bryden_years)
np.save("Output/to-pickle/RAPID_sine_fit_coeffs.npy",RAPID_sine_fit_coeffs)
np.save("Output/to-pickle/RAPID_AMOC_data.npy",RAPID_AMOC_data_smooth)
np.save("Output/to-pickle/RAPID_AMOC_monthly_climatology.npy",RAPID_AMOC_monthly_climatology)
np.save("Output/to-pickle/RAPID_time.npy",RAPID_time_smooth)
np.save("Output/to-pickle/RAPID_dates.npy",RAPID_dates_smooth)
