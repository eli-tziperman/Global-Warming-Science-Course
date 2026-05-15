# Make figure of two blackbody curves (Earth and Sun)
import numpy as np
import matplotlib.pyplot as plt 

# font required by PUP:,
plt.rcParams['font.family'] = 'Myriad Pro'
fontsize=9
plt.rcParams['font.size'] = fontsize

# constants:
c = 2.99792458*10**8
h = 6.62607004*10**-34
kb = 1.38*10**-23 #J/K

def plank_wavenumber(wavenum,t):
    wavenum = wavenum*100
    return 100*(2*h*c**2*np.power(wavenum,3))*np.power(np.exp(h*c*wavenum/(kb*t))-1,-1)

def plank_wavelength(wavelen,t):
    wavelen = wavelen/(10**9)
    exp_arg=np.minimum(h*c/(wavelen*kb*t),100.0);
    out=((2*h*c**2)/(wavelen**5))*1/(np.exp(exp_arg)-1)
    return out

nanos = np.arange(1,40000,1)

earth_rad = plank_wavelength(nanos,287)
sun_rad = plank_wavelength(nanos,5778)

fig = plt.figure(figsize=(5.6,2.1))
plt.subplot(1,2,1)

plt.title("(a) Black-body radiation",loc="center")

ln1 = plt.plot(nanos*10**-3,sun_rad,'red',label = "$T=5778$K (Sun)")
ax1 = plt.gca()

ax2 = ax1.twinx()
ln2 = ax2.plot(nanos*10**-3,earth_rad,'blue',label = "$T=287$K (Earth)")
ax2.set_ylim((0,1e7))

lns = ln1 + ln2
labs = [l.get_label() for l in lns]

ax1.set_xlabel('Wavelength ($\\mu m$)')
ax1.set_ylabel('Radiance') # W/m$^2$ (m$^{-1}$)')
ax1.set_ylim((0,2.8e13))
#ax2.set_ylabel('Radiance W/m$^2$ (m$^{-1}$)')

plt.legend(lns,labs,fontsize=fontsize-1)
ax1.tick_params(axis='y', colors='red')
ax2.tick_params(axis='y', colors='blue')
ax2.set_xticks(np.arange(-2,42,1), minor=True)

# add a vertical line at the main CO2 absorption band (15 micro meter):
CO2_wavelength_micrometer=15
CO2_wavenumber_inverse_cm=1/(100*CO2_wavelength_micrometer*1.e-6)
#print(CO2_wavelength_micrometer,CO2_wavenumber_inverse_cm)
plt.plot([CO2_wavelength_micrometer,CO2_wavelength_micrometer],[0,1e7]\
         ,lw=3,color=[0.8,0.8,0.8],zorder=-100)


plt.subplot(1,2,2)
OLR=np.load("Output/OLR_280ppm_all_gases.npy");
wavenumbers=np.load("Output/wavenumbers_all_gases.npy");
wavelength=(1/wavenumbers);
rad1 = plank_wavenumber(wavenumbers,287)
rad2 = plank_wavenumber(wavenumbers,260)
rad3 = plank_wavenumber(wavenumbers,220)

# Units of OLR modified to be consistent with Andrews, D. G. (2010).
# An introduction to atmospheric physics, Cambridge University Press:
plt.plot(wavenumbers,1000*OLR/np.pi,lw=0.5,color="blue");
plt.plot(wavenumbers,1000*rad1,lw=0.3,linestyle="--",color="black");
plt.plot(wavenumbers,1000*rad2,lw=0.3,linestyle="--",color="black");
plt.plot(wavenumbers,1000*rad3,lw=0.3,linestyle="--",color="black");
plt.annotate('287K', xy=(650,122), ha='center', va='center', rotation=-30)
plt.annotate('260K', xy=(900,50), ha='center', va='center', rotation=-40)
plt.annotate('220K', xy=(800,25), ha='center', va='center', rotation=-30)
plt.ylim(0,135)

# add a vertical line at the main CO2 absorption band (15 micro meter):
plt.plot([CO2_wavenumber_inverse_cm,CO2_wavenumber_inverse_cm],[0,135]\
         ,lw=3,color=[0.8,0.8,0.8],zorder=-100)

#plt.xlim(0,0.01)
plt.xlim(100,1500)
plt.title("(b) TOA OLR",loc="center")
plt.xlabel("Wavenumber (cm$^{-1}$)")
#plt.ylabel("Radiance") # mW\;m$^{-2}$ ster$^{-1}$ (cm$^{-1}$)$^{-1}$)
plt.tight_layout(pad=0)
fig.savefig('./Output/greenhouse-two_blackbodies.pdf')

plt.show()

