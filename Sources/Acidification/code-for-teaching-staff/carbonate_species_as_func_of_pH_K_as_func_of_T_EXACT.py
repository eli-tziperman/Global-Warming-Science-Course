#!/usr/bin/env python
# Plot exact solution (using mocsy library) for carbonate species as function of pH/total CO2.
# also reaction constants as function of temperature.

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
temp=15
sal=35
patm=1
depth=0
lat=30

#---------------------------------
# calculate equilibrium constants:
#---------------------------------
Kh, K1, K2, Kb, Kw, Ks, Kf, Kspc, Kspa, K1p, K2p, K3p, Ksi, St, Ft, Bt \
    = mocsy.mocsy.mconstants(temp, sal, patm, depth, lat \
                       , optt='Tinsitu', optp='m', optb="u74"\
                       , optk1k2='l', optkf="dg")

print("T=%g, S=%g, depth=%g, Kh=%g, K1=%g, K2=%g,  Kw=%g, Kspc=%g, Kspa=%g.\n"
      % (temp, sal, depth, Kh, K1, K2,  Kw, Kspc, Kspa))
print("units of dissociation constants are mol/kg approx mol/l.")

#-------------------------------------------
# 1st, plot carbonate species as alk varies:
#-------------------------------------------
myrange=np.arange(0.3,1.6,0.01)
N=len(myrange)
# initialize array of output values:
Valk=np.zeros(N)
VpH=np.zeros(N)
Vpco2=np.zeros(N)
Vfco2=np.zeros(N)
Vco2=np.zeros(N)
Vhco3=np.zeros(N)
Vco3=np.zeros(N)
i=-1
for alk in alk0*myrange:
    i=i+1
    pH,pco2,fco2,co2,hco3,co3,OmegaA,OmegaC,BetaD,DENis,p,Tis \
        =mocsy.mocsy.mvars(temp=temp, sal=sal, alk=alk, dic=dic0, 
                sil=0, phos=0, patm=patm, depth=depth, lat=lat, 
                optcon='mol/m3', optt='Tpot', optp='m')
    # mol/m^3 is same as mmol/liter!
    Valk[i]=alk
    VpH[i]=pH
    Vpco2[i]=pco2
    Vfco2[i]=fco2
    Vco2[i]=co2
    Vhco3[i]=hco3
    Vco3[i]=co3
    #print(pH,pco2,fco2,co2,hco3,co3)

# plot results:
plt.figure(1)
VtotCO2=Vhco3+Vco3+Vco2
plt.plot(VpH,Vhco3,label="HCO$_3^-$")
plt.plot(VpH,Vco3,label="CO$_3^{2-}$")
plt.plot(VpH,Vco2,label="CO$_2$")
plt.plot(VpH,VtotCO2,label="$\Sigma$CO$_2$")
plt.plot([8.2,8.2],[-0.1,2.1],color="k",linewidth=0.5\
         ,linestyle="--",label="Pre-indust pH")
plt.plot(VpH,Valk,"--",label="Alk")
plt.xlabel("pH")
plt.legend()
plt.title("fixed DIC")
plt.tight_layout()
plt.savefig("Output/Figure-Carbonate_species_as_func_of_pH_Fixed_DIC.pdf",format='pdf');
plt.pause(0.05)


#-------------------------------------------
# 2nd, plot carbonate species as DIC varies:
#-------------------------------------------
myrange=np.arange(0.5,2.4,0.01)
N=len(myrange)
# initialize array of output values:
alk_exact=np.zeros(N)
pH_exact=np.zeros(N)
pco2_exact=np.zeros(N)
fco2_exact=np.zeros(N)
co2_exact=np.zeros(N)
hco3_exact=np.zeros(N)
co3_exact=np.zeros(N)
i=-1
for dic in dic0*myrange:
    i=i+1
    pH,pco2,fco2,co2,hco3,co3,OmegaA,OmegaC,BetaD,DENis,p,Tis \
        = mocsy.mocsy.mvars(temp=temp, sal=sal, alk=alk0, dic=dic, 
                sil=0, phos=0, patm=patm, depth=depth, lat=lat, 
                optcon='mol/m3', optt='Tpot', optp='m')
    # mol/m^3 is same as mmol/liter!
    alk_exact[i]=alk0
    pH_exact[i]=pH
    pco2_exact[i]=pco2
    fco2_exact[i]=fco2
    co2_exact[i]=co2
    hco3_exact[i]=hco3
    co3_exact[i]=co3
    #print(pH,pco2,fco2,co2,hco3,co3)

# plot results:
plt.figure(2)
totCO2_exact=hco3_exact+co3_exact+co2_exact
plt.plot(pH_exact,hco3_exact,label="HCO$_3^-$")
plt.plot(pH_exact,co3_exact,label="CO$_3^{2-}$")
plt.plot(pH_exact,co2_exact,label="CO$_2$")
plt.plot(pH_exact,totCO2_exact,label="$\Sigma$CO$_2$")
plt.plot([8.2,8.2],[-0.1,2.1],color="k",linewidth=0.5\
         ,linestyle="--",label="pre-indust pH")
plt.plot(pH_exact,alk_exact,"--",label="alk")
plt.xlabel("pH")
plt.legend()
plt.title("fixed Alk")
plt.tight_layout()
plt.savefig("Output/Figure-Carbonate_species_as_func_of_pH_Fixed_Alk.pdf",format='pdf');
plt.pause(0.05)

# save variables to be pickled:
np.save("Output/to-pickle/Kh.npy",Kh)
np.save("Output/to-pickle/K1.npy",K1)
np.save("Output/to-pickle/K2.npy",K2)
np.save("Output/to-pickle/Kw.npy",Kw)
np.save("Output/to-pickle/Kspc.npy",Kspc)
np.save("Output/to-pickle/Kspa.npy",Kspa)
np.save("Output/to-pickle/exact_pH.npy",pH_exact)
np.save("Output/to-pickle/exact_hco3.npy",hco3_exact)
np.save("Output/to-pickle/exact_co3.npy",co3_exact)
np.save("Output/to-pickle/exact_co2.npy",co2_exact)
np.save("Output/to-pickle/exact_alk.npy",alk_exact)
np.save("Output/to-pickle/exact_pco2.npy",pco2_exact)


#-------------------------------------------------------------------
# 3rd, plot carbonate species as temperature varies, with fixed DEC:
#-------------------------------------------------------------------
# reference values for inputs:
dic0=2000*1028e-6 # mmol/l
alk0=2300*1028e-6 # mmol/l
# temp=15
sal=35
patm=1
depth=0
lat=30

my_Temperature_range=np.arange(10,20.01,0.01)
N=len(my_Temperature_range)
# initialize arrays of output values:
alk_variable_T=np.zeros(N)
pH_variable_T=np.zeros(N)
pco2_variable_T=np.zeros(N)
fco2_variable_T=np.zeros(N)
co2_variable_T=np.zeros(N)
hco3_variable_T=np.zeros(N)
co3_variable_T=np.zeros(N)
Kh_variable_T=np.zeros(N)
K1_variable_T=np.zeros(N)
K2_variable_T=np.zeros(N)
Kw_variable_T=np.zeros(N)
hco3_variable_T_approx=np.zeros(N)
co3_variable_T_approx=np.zeros(N)
H_variable_T_approx=np.zeros(N)
pH_variable_T_approx=np.zeros(N)
co2_variable_T_approx=np.zeros(N)
pco2_variable_T_approx=np.zeros(N)
#print("temp,\t pH,\t pco2,\t\t fco2,\t\t co2,\t\t hco3,\t co3")

i=-1
for temp in my_Temperature_range:
    i=i+1
    pH,pco2,fco2,co2,hco3,co3,OmegaA,OmegaC,BetaD,DENis,p,Tis \
        = mocsy.mocsy.mvars(temp=temp, sal=sal, alk=alk0, dic=dic0, 
                sil=0, phos=0, patm=patm, depth=depth, lat=lat, 
                optcon='mol/m3', optt='Tpot', optp='m')
    # mol/m^3 is same as mmol/liter!
    alk_variable_T[i]=1.0*alk0
    pH_variable_T[i]=1.0*pH
    pco2_variable_T[i]=1.0*pco2
    fco2_variable_T[i]=1.0*fco2
    co2_variable_T[i]=1.0*co2
    hco3_variable_T[i]=1.0*hco3
    co3_variable_T[i]=1.0*co3
    #print(temp,pH,pco2,fco2,co2,hco3,co3)
    
    Kh, K1, K2, Kb, Kw, Ks, Kf, Kspc, Kspa, K1p, K2p, K3p, Ksi, St, Ft, Bt \
        = mocsy.mocsy.mconstants(temp, sal, patm, depth, lat \
                                 , optt='Tpot', optp='m', optb="u74"\
                                 , optk1k2='l', optkf="dg")
    Kh_variable_T[i]=1.0*Kh
    K1_variable_T[i]=1.0*K1
    K2_variable_T[i]=1.0*K2
    Kw_variable_T[i]=1.0*Kw

    # approximate solution as function of temperature:
    # ------------------------------------------------
    # set reaction rates here, to make it convenient to set some of
    # them to a constant value and see which one is actually important
    # for the dependence on temperature:
    Kh=1.0*Kh_variable_T[i]
    K1=1.0*K1_variable_T[i]
    K2=1.0*K2_variable_T[i]
    Kw=1.0*Kw_variable_T[i]
    C_T=dic0*1.0
    alk=alk0*1.0
    hco3_variable_T_approx[i]=2*C_T-alk
    co3_variable_T_approx[i]=alk-C_T
    H_variable_T_approx[i]=K2*(2*C_T-alk)/(alk-C_T)
    pH_variable_T_approx[i]=-np.log10(H_variable_T_approx[i])
    co2_variable_T_approx[i]=(K2/K1)*(2*C_T-alk)**2/(alk-C_T) # this is $H_2CO_3^*$
    pco2_variable_T_approx[i]=1000*(K2/(K1*Kh))*(2*C_T-alk)**2/(alk-C_T)

    

# plot results:
plt.figure(3)
totCO2_variable_T=hco3_variable_T+co3_variable_T+co2_variable_T
plt.plot(my_Temperature_range,hco3_variable_T,label="HCO$_3^-$")
plt.plot(my_Temperature_range,co3_variable_T,label="CO$_3^{2-}$")
plt.plot(my_Temperature_range,co2_variable_T,label="CO$_2$")
plt.plot(my_Temperature_range,totCO2_variable_T,label="$\Sigma$CO$_2$")
plt.plot(my_Temperature_range,alk_variable_T,'--',label="alk")
plt.xlabel("Temperature (C)")
plt.legend()
plt.title("variable T")
plt.tight_layout()
plt.savefig("Output/Figure-Carbonate_species_as_func_of_Temperature_Fixed_Alk_and_DIC.pdf",format='pdf');
plt.pause(0.05)

plt.figure(4,figsize=(9,2.5))
props = dict(boxstyle='round', edgecolor="white", facecolor='white', alpha=1.0)

plt.subplot(1,3,1)
# reaction constants normalized by their value at the initial temperature:
Kw_variable_T=Kw_variable_T/Kw_variable_T[0]
K1_variable_T=K1_variable_T/K1_variable_T[0]
K2_variable_T=K2_variable_T/K2_variable_T[0]
Kh_variable_T=Kh_variable_T/Kh_variable_T[0]
plt.plot(my_Temperature_range,Kw_variable_T,label="$K_w$")
plt.plot(my_Temperature_range,K1_variable_T,label="$K_1$")
plt.plot(my_Temperature_range,K2_variable_T,label="$K_2$")
plt.plot(my_Temperature_range,Kh_variable_T,label="$K_h$")
plt.xlabel("Temperature (°C)")
plt.ylabel("$K(T)/K(T_0)$")
plt.xlim(10,20)
plt.legend()
plt.grid(lw=0.25)
plt.title("(a)",loc="left")
# ax1=plt.gca()
# ax1.text(0.5, 0.9, "(a)",transform=ax1.transAxes, fontsize=14,
#          horizontalalignment='center',verticalalignment='center', bbox=props)

plt.subplot(1,3,2)
# pH:
plt.plot(my_Temperature_range,pH_variable_T,color="b",label="pH")
#plt.plot(my_Temperature_range,pH_variable_T_approx,'--',color="b",label="pH")
plt.xlabel("Temperature (°C)")
plt.ylabel("pH")
plt.xlim(10,20)
plt.grid(lw=0.25)
plt.title("(b)",loc="left")
#ax1=plt.gca()
#ax1.text(0.5, 0.9, "(b)",transform=ax1.transAxes, fontsize=14,
#         horizontalalignment='center',verticalalignment='center', bbox=props)

plt.subplot(1,3,3)
# pCO2:
plt.plot(my_Temperature_range,pco2_variable_T,color="b",label="pCO$_2$")
#plt.plot(my_Temperature_range,pco2_variable_T_approx,'--',color="b",label="pCO$_2$")
plt.xlabel("Temperature (°C)")
plt.ylabel("pCO$_2$ (ppm)")
plt.xlim(10,20)
plt.grid(lw=0.25)
plt.title("(c)",loc="left")
#ax1=plt.gca()
#ax1.text(0.5, 0.9, "(c)",transform=ax1.transAxes, fontsize=14,
#         horizontalalignment='center',verticalalignment='center', bbox=props)

plt.tight_layout(w_pad=0.01)
plt.savefig("Output/acidification-pH-pCO2-K_as_func_of_Temperature_Fixed_Alk_and_DIC.pdf",format='pdf');
plt.show()
