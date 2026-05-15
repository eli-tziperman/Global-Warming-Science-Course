"""
This code compares the CO2 concentrations due to the 1990 IPCC 'SP92
emission scenarios' to the observed CO2 since those scenarios were
formulated. are we on the worst-case-scenario?

The CO2 was estimated from the emission scenario using a carbon model
in the following work:

Balancing the carbon budget. Implications for projections of future carbon dioxide concentration changes. T. M. L. WIGLEY, 1993.
https://doi.org/10.1034/j.1600-0889.1993.t01-4-00002.x

and this code plots the observed CO2 record over the figure from this
publication that shows the estimated CO2 time series.

"""

import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
import matplotlib
import pickle

past=np.loadtxt("Input/co2_data.txt")

data_past = open("Input/past_concentrations.pickle","rb")
data_future = open("Input/future_concentrations.pickle","rb")
dict_past = pickle.load(data_past)
dict_future =pickle.load(data_future)

fig = plt.figure(1,figsize=(12,12))
plt.rcParams['figure.dpi']= 600
img = plt.imread("Input/wigley-1993.png")
ax=plt.gca()
ax.imshow(img, extent=[1990, 2100, 350, 1000],aspect='auto')
plt.xlim(1990,2100)
plt.ylim(350,1000)
print(dict_past.keys())
print(dict_future.keys())
plt.plot(past[:,0],past[:,1],lw=3,color="blue")
#plt.plot(dict_past['past_years_CO2'], dict_past['past_conc_CO2'])
plt.plot(dict_future['future_years'],dict_future['future_conc_CO2'],lw=1,color="red")
plt.legend(['Past CO2','Projected CO2'])
plt.xlabel('Year')
plt.ylabel('Concentration (ppm)')
plt.show();
