"""
A script that loads the .npy files and plots them to ensure the data
is correct.

Produces several plots that should be similar to the plots produced
by drought_data_organizer.py, but has no useful original output. 
Potentially useful as an example program.

Yonathan Vardi 2019-07-25
"""

import numpy as np
import matplotlib.pyplot as plt

dir = "./Output/"

#load the sa[H]el [G]FDL [E]vaporation, [P]recipitation, and [M]oisture data
hge = np.load(dir+"sahel_gfdl_evaporation.npy")
hgp = np.load(dir+"sahel_gfdl_precipitation.npy")
hgm = np.load(dir+"sahel_gfdl_moisture.npy")
#load the sa[H]el [M]IROC [E]vaporation, [P]recipitation, and [M]oisture data
hme = np.load(dir+"sahel_miroc_evaporation.npy")
hmp = np.load(dir+"sahel_miroc_precipitation.npy")
hmm = np.load(dir+"sahel_miroc_moisture.npy")
#load the south[W]est [G]FDL [E]vaporation, [P]recipitation, and [M]oisture data
wge = np.load(dir+"sw_gfdl_evaporation.npy")
wgp = np.load(dir+"sw_gfdl_precipitation.npy")
wgm = np.load(dir+"sw_gfdl_moisture.npy")
#load the south[W]est [M]IROC [E]vaporation, [P]recipitation, and [M]oisture data
wme = np.load(dir+"sw_miroc_evaporation.npy")
wmp = np.load(dir+"sw_miroc_precipitation.npy")
wmm = np.load(dir+"sw_miroc_moisture.npy")

#create the plots
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(nrows=2, ncols=3,figsize=(8,4))
#title all the subplots
ax1.set_title("sahel evaporation")
ax2.set_title("sahel precipitation")
ax3.set_title("sahel moisture")
ax4.set_title("sw evaporation")
ax5.set_title("sw precipitation")
ax6.set_title("sw moisture")

plt.ioff()

#draw the plots
#on each subplot, plot the relevant data from both models
ax1.plot(hge[0], hge[1])
ax1.plot(hme[0], hme[1])

ax2.plot(hgp[0], hgp[1])
ax2.plot(hmp[0], hmp[1])

ax3.plot(hgm[0], hgm[1])
ax3.plot(hmm[0], hmm[1])

ax4.plot(wge[0], wge[1])
ax4.plot(wme[0], wme[1])

ax5.plot(wgp[0], wgp[1])
ax5.plot(wmp[0], wmp[1])

ax6.plot(wgm[0], wgm[1])
ax6.plot(wmm[0], wmm[1])
#show the plots
plt.tight_layout()

## save as pdf:
plt.savefig("Output/Figures/droughts-timeseries-for-data-verification.pdf",format='pdf');
plt.show()
