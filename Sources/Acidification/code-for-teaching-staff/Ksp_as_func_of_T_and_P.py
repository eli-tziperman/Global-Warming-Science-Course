#!/usr/bin/env python
# Plot exact solution (using mocsy library) for carbonate species as function of pH/total CO2.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import mocsy.mocsy
import pickle

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

def pickle_variables(fileName, env, *variables):
    d = dict([(x, env[x]) for v in variables for x in env if v is env[x]])
    with open(fileName, 'wb') as f:
        pickle.dump(d, f)

# reference values for inputs:
dic0=2000*1028e-6 # mmol/l
alk0=2300*1028e-6 # mmol/l
temp=np.arange(0,31,1)
sal=35
patm=1
depth=np.arange(0,4200,200)
lat=30

K_spa=np.zeros((len(temp),len(depth)));
# calculate equilibrium constants:
iT=-1;
for T in temp:
    iT=iT+1
    iz=-1
    for z in depth:
        iz=iz+1
        Kh, K1, K2, Kb, Kw, Ks, Kf, Kspc, Kspa, K1p, K2p, K3p, Ksi, St, Ft, Bt \
            = mocsy.mocsy.mconstants(T, sal, patm, z, lat \
                                     , optt='Tinsitu', optp='m', optb="u74"\
                                     , optk1k2='l', optkf="dg")
        K_spa[iT,iz]=Kspa

fig=plt.figure(figsize=(4,3.3),dpi=300)
plt.contourf(temp,depth/1000,K_spa.T*1.e6)
plt.colorbar()
plt.xlabel("Temperature (°C)")
plt.ylabel("Depth (km)")
#plt.title("$\\rm K_{sp}$ for aragonite $\\times10^6$")
plt.tight_layout()
fig.savefig("Output/acidification-Ksp_as_func_of_T_and_P.pdf")
plt.show()
