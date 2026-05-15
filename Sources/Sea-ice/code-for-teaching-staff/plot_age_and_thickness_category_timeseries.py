import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import cm

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

# read sea ice age for all years, and axes:
# -----------------------------------------
lon = np.load("Output/to-pickle/sic_age_obs_lon.npy")
lat = np.load("Output/to-pickle/sic_age_obs_lat.npy")
Ncateg=6
Nyears=2024-1984+1
age_categories=np.zeros((Nyears,Ncateg))
years=range(1984,2025)
iyear=-1
for year in years:
    iyear=iyear+1
    # get age data for this year:
    age=np.load("Output/age_npy/sic_age_obs"+repr(year)+".npy")

    # set age to NaN for values larger than 15 which indicate
    # something other than age, and for latitudes south of 70N:
    age1=1.0*age
    age1[age>15]=np.nan
    age1[age==0]=np.nan
    age1[lat<70]=np.nan
    age=age1*1.0

    # mask indicating location of sea ice (1), vs open ocean points (0) 
    age_mask=np.zeros(age.shape)+1
    age_mask[np.isnan(age)]=0 # 1 for ice points, 0 for not
    N_ice_points=np.sum(age_mask)

    # calculate number of grid point in each age category:
    for iage in range(1,Ncateg+1):
        if iage<Ncateg:
            age_categories[iyear,iage]=np.sum(age_mask[age<=iage])/N_ice_points
        else:
            age_categories[iyear,iage-1]=1

# plot age categories:
# --------------------
fig=plt.figure(1,figsize=(6,3))
color=['b','c','g','y','r','m']

# get rainbow colors:
norm = matplotlib.colors.Normalize(vmin=0, vmax=6)
colors=np.zeros((6,4))
for i in range(0,6):
    colors[i]=cm.jet(norm(i),bytes=True)
colors=1*colors[:,:3]/255

plt.subplot(1,2,1)

for iage in range(0,Ncateg):
    plt.fill_between(years, age_categories[:,iage], age_categories[:,iage-1],color=tuple(colors[iage,:]))
    plt.plot(years, age_categories[:,iage],label=repr(iage+1),color='k')
plt.title('(a) Age (years)',loc="left");
plt.xlabel("Year")
plt.ylabel("Fraction")
ax=plt.gca()
ax.set_xticks(range(1985,2025,1), minor=True)
plt.xlim([1984,2024])
plt.ylim([0.0,1])
plt.yticks(np.arange(0.0,1.1,0.1))

# place text boxes with categories on plot:
props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
x=0.22
ax.text(x, 0.25, '$<1$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.56, '$<2$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.68, '$<3$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.77, '$<4$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.93, '$>4$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)


# read grid information:
# ----------------------
lon = np.load("Output/to-pickle/sic_thickness_obs_lon.npy")
lat = np.load("Output/to-pickle/sic_thickness_obs_lat.npy")
cell_area=np.load("Output/to-pickle/sic_thickness_obs_cell_area.npy")

# read and process sea ice thickness for all years:
# -------------------------------------------------
Ncateg=6
Nyears=2024-1984+1
thickness_categories=np.zeros((Nyears,Ncateg))
years=range(1984,2025)
iyear=-1
for year in years:
    iyear=iyear+1
    # get thickness data for this year:
    thickness=np.load("Output/thickness_npy/sic_thickness_obs"+repr(year)+".npy")

    # set thickness to NaN for values larger than 15 which indicate
    # something other than thickness, and for latitudes south of 70N:
    thickness1=1.0*thickness
    thickness1[thickness>15]=np.nan
    thickness1[thickness==0]=np.nan
    thickness1[lat<70]=np.nan
    thickness=thickness1*1.0

    # mask indicating location of sea ice (1), vs open ocean points (0) 
    thickness_mask=np.zeros(thickness.shape)+1
    thickness_mask[np.isnan(thickness)]=0 # 1 for ice points, 0 for not
    cell_area_this_year=np.zeros(thickness_mask.shape)
    for imonth in range(0,12):
        cell_area_this_year[:,:,imonth]=cell_area[:,:]*thickness_mask[:,:,imonth]
    total_ice_area_this_year=np.nansum(cell_area_this_year)
    N_ice_points=np.sum(thickness_mask)

    # calculate number of grid point in each thickness category:
    for ithickness in range(1,Ncateg+1):
        if ithickness<Ncateg:
            thickness_categories[iyear,ithickness]= \
                np.sum(cell_area_this_year[thickness<=ithickness] \
                       *thickness_mask[thickness<=ithickness]) \
                       /total_ice_area_this_year
        else:
            thickness_categories[iyear,ithickness-1]=1

# plot thickness categories:
# --------------------------
plt.subplot(1,2,2)

color=['b','c','g','y','r','m']
for ithickness in range(0,Ncateg):
    plt.fill_between(years, thickness_categories[:,ithickness], thickness_categories[:,ithickness-1],color=tuple(colors[ithickness,:]))
    plt.plot(years, thickness_categories[:,ithickness],label=repr(ithickness+1),color='k')
plt.title('(b) Thickness (m)',loc="left");
plt.xlabel("Year")
plt.ylabel("Fraction")
ax=plt.gca()
ax.set_xticks(range(1985,2025,1), minor=True)
plt.xlim([1984,2024])
plt.ylim([0.0,1])
plt.yticks(np.arange(0.0,1.1,0.1))

# place text boxes with categories on plot:
props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
x=0.13
ax.text(x, 0.15, '$<1$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.37, '$<2$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.62, '$<3$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.88, '$<4$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.text(x, 0.99, '$>4$', transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)


plt.tight_layout()
plt.pause(1.0)

fig.savefig("Output/sea-ice-age-and-thickness-categories-timeseries.pdf")
