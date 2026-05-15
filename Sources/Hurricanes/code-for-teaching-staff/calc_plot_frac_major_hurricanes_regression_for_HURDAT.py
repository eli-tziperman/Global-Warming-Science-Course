# Written by Veer Gadodia veergadodia24@gmail.com, summer 2020
# Further edited by Eli.
# Reproducing the results of:
#@article{Kossin-Knapp-Olander-et-al-2020:global,
#  title =	 {Global increase in major tropical cyclone exceedance
#                  probability over the past four decades},
#  author =	 {Kossin, James P and Knapp, Kenneth R and Olander,
#                  Timothy L and Velden, Christopher S},
#  journal =	 {Proceedings of the National Academy of Sciences},
#  year =	 2020,
#  publisher =	 {National Acad Sciences}
#}

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import copy as copy
from scipy import stats
import pymannkendall as mk

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

# Options -- Set doThreeYearBins to true or false
doThreeYearBins = False

region = "Global"  # Options - Global,  EP (Eastern North Pacific), WP (Western North Pacific), SP (South Pacific), NI (Northern Indian), SI(Southern Indian), NA (North Atlantic)

# Importing the datasets
dataset = pd.read_csv('../../../Data-for-teaching-staff/Hurricanes/ADT-HURSAT/pnas.1920849117.sd08.csv')
data = dataset.iloc[:, :].values

dataset = pd.read_csv('../../../Data-for-teaching-staff/Hurricanes/ADT-HURSAT/pnas.1920849117.sd09.csv')
years_data = dataset.iloc[:, :].values

if region != "Global":
    dataset = pd.read_csv('../../../Data-for-teaching-staff/Hurricanes/ADT-HURSAT/pnas.1920849117.sd01.csv',dtype=str, na_values=[], keep_default_na=False)
    region_data = dataset.iloc[:].values


# Use list comprehension to create array for years on the x axis
if doThreeYearBins:
    x_axis = np.arange(1980, 2018, 3)
else:
    x_axis = np.arange(1979, 2018, 1)
    x_axis=1.0*np.delete(x_axis,1)

HURSAT_years=copy.deepcopy(years_data)
HURSAT_wind_speed=copy.deepcopy(data)
HURSAT_years_axis=copy.deepcopy(x_axis)
np.save("Output/HURSAT_years.npy",HURSAT_years)
np.save("Output/HURSAT_wind_speed.npy",HURSAT_wind_speed)

# Create dictionary where keys are the years and the value is an array
# containing number of major hurricanes and number of hurricanes
Hurricanes_per_year = {}
for yr in HURSAT_years_axis:
    Hurricanes_per_year[yr] = [0, 0]

# Loop through every windspeed of every hurricane. If greater than 100
# knots, increase major hurricane and total hurricane count by 1, 
# else if greater than 65 knots, increase only total hurricane count by 1
for ind, hurricane_6hourly_winds in enumerate(HURSAT_wind_speed):
    year = int(HURSAT_years[ind][0])

    # Exclude years 1978 and 1980
    if year > 1978 and year != 1980:
        if region == "Global":
            if doThreeYearBins:
            # Converts year to the closest one on the HURSAT_years_axis since we are
            # averaging the data in groups of 3 years
                if year % 3 == 1:
                    year -= 1
                elif year % 3 == 2:
                    year += 1

            for windspeed in hurricane_6hourly_winds:
                if windspeed >= 100:
                    Hurricanes_per_year[year][0] += 1
                    Hurricanes_per_year[year][1] += 1
                else:
                    if windspeed >= 65:
                        Hurricanes_per_year[year][1] += 1
        else:  # if not Global
            if region == region_data[ind][0]:
                if doThreeYearBins:
                # Converts year to the closest one on the HURSAT_years_axis since we are
                # averaging the data in groups of 3 years
                    if year % 3 == 1:
                        year -= 1
                    elif year % 3 == 2:
                        year += 1

                for windspeed in hurricane_6hourly_winds:
                    if windspeed >= 100:
                        Hurricanes_per_year[year][0] += 1
                        Hurricanes_per_year[year][1] += 1
                    else:
                        if windspeed >= 65:
                            Hurricanes_per_year[year][1] += 1


fraction_major_hurricanes_per_year = []
for key, value in Hurricanes_per_year.items():
    if value[1] != 0:
        fraction_major_hurricanes_per_year.append(value[0]/value[1])
    else:
        print("found zero value[1]",key,value)


# calculate linear regresion line:
slope, intercept, r_value, p_value, std_err = stats.linregress(HURSAT_years_axis, fraction_major_hurricanes_per_year)
y=intercept+slope*HURSAT_years_axis
print("linear regression diagnostics:")
print("Slope: {}".format(slope))
print("Intercept: {}".format(intercept))
print("R-squared: {}".format(r_value**2))
print("p-value: {}".format(p_value))

# Mann Kendall test:
trend, h, p_value, z, Tau, s, var_s, slope, intercept = mk.original_test(fraction_major_hurricanes_per_year)
print("Mann Kendall diagnostics:")
print("Tau: {}".format(Tau))
print("p-value: {}".format(p_value))

# Plot:
# -----
fig=plt.figure(figsize=(5,3),dpi=300)
ax=plt.gca()
plt.scatter(HURSAT_years_axis, fraction_major_hurricanes_per_year)
plt.plot(HURSAT_years_axis, fraction_major_hurricanes_per_year, linewidth=1)
plt.xlabel ("Year")
plt.ylabel ("Fraction major hurricanes")
plt.xlim(1977,2020)
r2_int=int(np.round(100*r_value**2))
plt.text(0.1,0.85, f'{region}\n$ r^2={r2_int}\\% $'
         , transform=ax.transAxes
         , bbox=dict(boxstyle='round', facecolor='white', edgecolor='white', alpha=1.0)
         )

# Plot the linear fit
plt.plot(HURSAT_years_axis, y, c='r', linewidth=2)
plt.grid(lw=0.25)

plt.tight_layout()
fig.savefig("Output/hurricanes-fraction-major-hurricanes-timeseries-%s.pdf" % region)
plt.show()
