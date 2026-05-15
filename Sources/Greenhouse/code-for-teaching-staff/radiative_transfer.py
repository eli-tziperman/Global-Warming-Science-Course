#!/usr/bin/env python
# coding: utf-8
########################################################################
# A line-by-line radiative calculation of OLR given CO2 and other
# greenhouse concentrations.
# Camille Hankel, 201910
# This is called by run_all.py
########################################################################

import numpy as np
import matplotlib.pyplot as plt 
from math import *
from scipy.special import jv,yv
from scipy.integrate import quad
from scipy.special import wofz
import pandas as pd
import time
import sys
#from scipy import signal
#import pickle

# get command line arguments: gas_list and co2_conc
input_arguments=sys.argv
co2_conc=int(input_arguments[1])
gas_list=input_arguments[2:]
print("input arguments: CO2_conc=",co2_conc,", gas_list=",gas_list)

# constants DON'T CHANGE
# E = 106.13 #cm^1
c2 = 1.4387770 #cm K
c_erg = 2.99792458*10**10 #cm s^-1 for Hitran calc
c = 2.99792458*10**8
k = 1.3806488*10**-16 #ergK−1
NA = 6.02214129*10**23 #mol^-1
h = 6.62607004*10**-34
kb = 1.38*10**-23 #J/K
R = 297
cp = 1040
T1 = 170
g = 9.81
TREF = 296
PSURF = 1 #atm
cutoff = 25

#------------------------------------------------------------------------
### ONLY CHANGE THESE PARAMETERS ###
start_wavenum =.1 # default is .1
end_wavenum = 2000  # default is 2000
spect_res = .1    # default is .1

# set gas_list and co2_conc if they are not defined:
try:
    gas_list
except NameError:
    gas_list=['CO2','CH4','H2O','O3']
try:
    co2_conc
except NameError:
    co2_conc = 280
#------------------------------------------------------------------------

# set file name for output:
if 'H2O' in gas_list:
    FileNameExtension="_"+repr(co2_conc)+"ppm_"+"all_gases"
else:
    FileNameExtension="_"+repr(co2_conc)+"ppm_""CO2_only"
OutputFileName="./Output/to-pickle/OLR"+FileNameExtension+".npy"
print("OutputFileName=",OutputFileName)

    
# Atmospheric profiles from Anderson et al 1986
p_list = [101300,89880,79500,70120,61660,54050,47220,41110,35650,30800,26500,22700,19400,16580,14170,12110,10350,8850,7565,6467,5529,4729,4047,3467,2972,2549,1743,1197,801,574.6,415,287.1,206,149.1,109,79.78]
T_list = [288.2,281.7,275.2,268.7,262.2,255.7,249.2,242.7,236.2,229.7,223.3,216.8,216.7,216.7,216.7,216.7,216.7,216.7,216.7,216.7,216.7,217.6,218.6,219.6,220.6,221.6,224,226.5,230,236.5,242.9,250.4,257.3,264.2,270.6,270.7]
Z_list = [0.0,1.0,2.0,3.0,4.0,5.06,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,27.5,30,31,32.5,35,37.5,40,42.5,45,47.5,50]
T0 = T_list[0]

# Initialize dictionary that will store gas-specific information from H
vij_dict = {'CO2':None,'H2O':None,'CH4':None,'O3':None}
sig_ref_dict = {'CO2':None,'H2O':None,'CH4':None,'O3':None}
gam_L_dict = {'CO2':None,'H2O':None,'CH4':None,'O3':None}
nair_dict = {'CO2':None,'H2O':None,'CH4':None,'O3':None}
E_dict = {'CO2':None,'H2O':None,'CH4':None,'O3':None}

# Atmospheric gas concentrations from Anderson et al 1986
conc_dict = {'CO2':[co2_conc*1e-6]*36, 'H2O':None,'CH4':None,'O3':None}
conc_dict['H2O'] = [7750e-6,6070e-6,4630e-6,3180e-6,2160e-6,1400e-6,925e-6,572e-6,367e-6,158e-6,70e-6,36.1e-6,19.1e-6,10.9e-6,5.93e-6,5e-6,3.95e-6,3.85e-6,3.83e-6,3.85e-6,3.90e-6,3.98e-6,4.07e-6,4.2e-6,4.30e-6,4.43e-6,4.58e-6,4.73e-6,4.83e-6,4.9e-6,4.95e-6,5.03e-6,5.15e-6,5.23e-6,5.25e-6,5.23e-6]
conc_dict['O3'] = [.0266e-6,.0293e-6,.0324e-6,.0332e-6,.0339e-6,.0377e-6,.0411e-6,.0501e-6,.0597e-6,.0917e-6,.131e-6,.215e-6,.31e-6,.385e-6,.503e-6,.651e-6,.87e-6,1.19e-6,1.59e-6,2.03e-6,2.58e-6,3.03e-6,3.65e-6,4.17e-6,4.63e-6,5.12e-6,5.8e-6,6.55e-6,7.37e-6,7.84e-6,7.8e-6,7.3e-6,6.2e-6,5.25e-6,4.1e-6,3.1e-6]
conc_dict['CH4'] = [1.7e-6,1.7e-6,1.7e-6,1.7e-6,1.7e-6,1.7e-6,1.7e-6,1.7e-6,1.7e-6,1.69e-6,1.69e-6,1.68e-6,1.66e-6,1.65e-6,1.63e-6,1.61e-6,1.58e-6,1.55e-6,1.52e-6,1.48e-6,1.42e-6,1.36e-6,1.27e-6,1.19e-6,1.12e-6,1.06e-6,.987e-6,.914e-6,.83e-6,.746e-6,.662e-6,.564e-6,.461e-6,.363e-6,.277e-6,.21e-6]

molar_mass = {'CO2':43.9898,'H2O':18.01,'CH4':16.03,'O3':47.985}


# Calculates the line broadening for a specific spectral line, uses the special
# function wofz for the convolution of a gaussian and a lorentzian. Ignored nature
# broadening. 
def f_V(x,vij,p,pself,t,Tref,m,nair,gam_L):
    gamma = (Tref/t)**nair*gam_L*(p-pself)
    alpha_d = vij/c_erg * sqrt(2*NA*k*t*log(2)/m)
    sigma = alpha_d/(np.sqrt(2*log(2)))
    z = (x-vij+gamma*1j)/(sigma*np.sqrt(2))
    ans = (wofz(z).real)/(sigma*np.sqrt(2*np.pi))
    return ans

# Takes the broadened line shape and multiplies it by the proper magnitude depending
# on pressure, temperature, etc. 
def sig_ij(y,vij,p,pself,t,Tref,m,Sij_Tref,nair,gam_L,E):
    Sij = Sij_Tref*(Tref/t)**1.5*exp(-c2*E/t)*(1-exp(-c2*vij/t))/(exp(-c2*E/Tref)*(1-exp(-c2*vij/Tref)))
    sig_ij = Sij*f_V(y,vij,p,pself,t,Tref,m,nair,gam_L)
    return sig_ij

# calculates the absorption cross-section for the full spectrum, using HITRAN data
def absorption_Xsection(y,vij_list,nair_list,sig_ref_list,gam_L_list,E_list,P,PSELF,T,tref,m):
    total_spec = np.zeros((len(y),))
    t1 = time.time()
    for i in range(len(vij_list)):
        line_center = vij_list[int(i)]
        sig_ref = sig_ref_list[i]
        nair = nair_list[i]
        gam_L = gam_L_list[i]
        E = E_list[i]
        range_25 = np.where(abs(y-line_center) < cutoff)
        sig = np.array(sig_ij(y[range_25],line_center,P,PSELF,T,tref,m,sig_ref,nair,gam_L,E))
        if np.sum(np.isnan(sig)) != 0:
            print('problem!')
        total_spec[range_25] += sig
        
    t2 = time.time()

    return total_spec

def f(nu):
	return 12.17 -.051*nu + 8.32*10**-5*nu**2 - 7.07*10**-8*nu**3+2.33*10**-11*nu**4

def kap_cont(nu,T):
	return np.exp(f(nu))*(296/T)**4.25

def plank(wavenum,t):
    wavenum = wavenum*100
    return 100*(2*h*c**2*np.power(wavenum,3))*np.power(np.exp(h*c*wavenum/(kb*t))-1,-1)

# calculates tau (optical depth) for each level of the atmosphere, which requires
# calling the function to calculate the absorption cross-section
def get_tau(M,pp,nu,vij_list,nair_list,sig_ref_list,gam_L_list,E_list):
    kap_mx = np.zeros((len(nu),len(p_list)))
    tau_list_temp = np.zeros((len(nu),len(p_list)))
    M2 = M/1000
    
    for i in range(len(p_list)-1):
        p = p_list[i+1]
        dp = p_list[i] - p_list[i+1]
        dpp = abs(p_list[i]*pp[i] - p_list[i+1]*pp[i+1])
        conc_avg = (pp[i+1] + pp[i])/2
        T = T_list[i+1]
        # Get pressure in atm to plug into absorption_Xsection
        p_atm = p/p_list[0]
        # Convert from cm^2/molecule to m^2/kg
        kap = (NA/10000)*(1/M2)*absorption_Xsection(nu,vij_list,nair_list,sig_ref_list,gam_L_list,E_list,p_atm,conc_avg*p_atm,T,TREF,M)
        if gas != 'H2O':
            dtau = kap*(M/28)*dpp/g
        else:
            dtau = kap*(M/28)*dpp/g*(p+p_list[i])/(2*p_list[0])
            if np.sum(np.where(dtau < 0))>0:
                print('problem!')
            
        kap_mx[:,i+1] = kap
        tau_list_temp[:,i+1] = tau_list_temp[:,i] + dtau
    
    return (tau_list_temp, tau_list_temp[:,-1],kap_mx)
   
# Read in HITRAN data and get list of line centers,etc. for each gas
def read_data(start_wavenum,end_wavenum,vij_dict,sig_ref_dict,gam_L_dict,nair_dict,E_dict):
    for gas in vij_dict.keys():
        filename = '../../../Data-for-teaching-staff/Greenhouse/data_HITRAN/'+gas+'.par.gz'
        data = pd.read_fwf(filename, widths=[2,1,12,10,10,5,5,10,4,8,3,3,9,9,3,6] \
                           ,header=None, compression="gzip")
        iso1 = data.loc[data[1] ==1] # take only first isotopologue
        iso1range = iso1.loc[(iso1[2]>=start_wavenum)&(iso1[2]<=end_wavenum)] # wavenumber range of interest

        # All info we need from filen stored in dictionaries
        vij_dict[gas] = np.array(iso1range[2])
        sig_ref_dict[gas] = np.array(iso1range[3])
        gam_L_dict[gas] = np.array(iso1range[5])
        nair_dict[gas] = np.array(iso1range[8])
        E_dict[gas] =  np.array(iso1range[7])

    print("Total number of line centers to calculate: ",str(sum([len(vij_dict[gas]) for gas in vij_dict.keys()])))
    
    return


# In[5]:


# Read data of absorption lines for all 4 gases
read_data(start_wavenum,end_wavenum,vij_dict,sig_ref_dict,gam_L_dict,nair_dict,E_dict)

# Tau stored in a pressure-level by wavenumber array
nu = np.arange(start_wavenum,end_wavenum,spect_res)
tau_list = np.zeros((len(nu),len(p_list),4))
tau_inf = np.zeros((len(nu),4))
kap_list = np.zeros((len(nu),len(p_list),4))
# Get tau for each gas at each level of the atmosphere 
i = 0
for gas in gas_list: #change if you want to exclude some gases from calculation
    print('working on: ', gas)
    M = molar_mass[gas]
    pp = conc_dict[gas]
    vij_list = vij_dict[gas]
    sig_ref_list = sig_ref_dict[gas]
    gam_L_list = gam_L_dict[gas]
    nair_list = nair_dict[gas]
    E_list = E_dict[gas]
    
    (gas_tau, gas_tau_inf,kap_mx) = get_tau(M,pp,nu,vij_list,nair_list,sig_ref_list,gam_L_list,E_list)
    
    kap_list[:,:,i] = kap_mx
    tau_list[:,:,i] = gas_tau
    tau_inf[:,i] = gas_tau_inf
    i+=1
    
# Get total tau by adding together tau from each gas
tau_total = np.sum(tau_list,axis=2)
tau_inf_total = np.sum(tau_inf,axis=1)

# Allocate arrays to store upwelling each level and wavenumber
F = np.zeros((len(nu),len(p_list)))
total_F = np.zeros((len(nu),))

#loop over vertical levels to solve for integral
for i in range(len(p_list)-1):
    tau = tau_total[:,i+1]
    p = p_list[i+1]
    T = T_list[i+1]
    B = plank(nu,T)
    dtrans = np.exp(tau-tau_inf_total) - np.exp(tau_total[:,i] - tau_inf_total)
    contribution = np.pi*B*dtrans
    total_F = total_F +contribution
    F[:,i+1] = contribution

total_F += np.pi*plank(nu,T0)*np.exp(-tau_inf_total)


# Apply a little bit of smoothing for clarity
df = pd.DataFrame(columns=['OLR'])
df['OLR'] = total_F
smooth_OLR2 = df['OLR'].rolling(window=40).mean()

# The smoothing introduces some NaNs, save only the parts
# that are not NaN:
wavenumbers=nu[~np.isnan(smooth_OLR2)]
smooth_OLR_no_nans=smooth_OLR2[~np.isnan(smooth_OLR2)]
np.save(OutputFileName, smooth_OLR_no_nans)
np.save("./Output/to-pickle/wavenumbers.npy",wavenumbers)

# Plot OLR and blackbody curves for reference
fig = plt.figure(figsize=(11, 8))
plt.plot(nu,smooth_OLR2)
plt.plot(nu,np.pi*plank(nu,T0))
plt.plot(nu,np.pi*plank(nu,216))
plt.plot(nu,np.pi*plank(nu,260))
plt.xlabel('Wavenumber $cm^{-1}$')
plt.ylabel('Radiation $W/m^2$')
plt.ylim((0,.5))
plt.legend(['OLR at TOA','Blackbody at 288K','Blackbody at 260','Blackbody at 216K'])
H = plt.gcf()
H.savefig('./Output/Figure-greenhouse-OLR_smoothed_zoomout'+FileNameExtension+'.pdf')
plt.show(block=False)

# In[8]:


print('Total OLR for '+str(co2_conc)+'ppm CO2:',round(np.nansum(total_F*spect_res),3), r'W/m^2')


fig = plt.figure(figsize=(11,8))
plt.loglog(conc_dict['CH4'],p_list)
plt.loglog(conc_dict['H2O'],p_list)
plt.loglog(conc_dict['O3'],p_list)
plt.gca().invert_yaxis()
plt.legend(['$CH_4$','$H_2O$','$O_3$'],fontsize=14)
# plt.title('Mixing Ratio Profiles')
plt.ylabel('Pressure [Pa]',fontsize=16)
plt.xlabel('Mixing Ratio',fontsize=16)
H = plt.gcf()
H.savefig('./Output/Figure-greenhouse-MixingRatioProfiles'+FileNameExtension+'.pdf')
plt.show(block=False)


# Plot temperature profile used
fig = plt.figure(figsize=(8,6))
ax = plt.gca()
ax.semilogy(T_list,p_list)
plt.gca().invert_yaxis()
ax.set_ylabel('Pressure [Pa]',fontsize=16)
ax.set_xlabel('Temperature [K]',fontsize=16)
ax2 = ax.twinx()
ax2.set_ylim((0,50))
ax2.set_ylabel('Height [km]')
H = plt.gcf()
H.savefig('./Output/Figure-greenhouse-TempProfile'+FileNameExtension+'.pdf')
plt.show(block=False)


# Make plot of absorption cross-section for CO2
i=0
for gas in gas_list:
    fig = plt.figure(figsize=(11,8))
    plt.rcParams.update({'font.size':18})
    #-10 -- an abitrarily chosen pressure level at which to display kappa:
    plt.semilogy(nu,kap_list[:,-10,i],linewidth=.9)
    plt.xlabel('Wavenumber [$cm^{-1}$]')
    plt.ylabel('Absorption Cross Section [$m^2/kg$]')
    H = plt.gcf()
    plt.title(gas)
    H.savefig('./Output/Figure-greenhouse-cross-section_CO2='+repr(co2_conc)+'_'+gas+'.pdf')
    plt.show(block=False)
    i=i+1

