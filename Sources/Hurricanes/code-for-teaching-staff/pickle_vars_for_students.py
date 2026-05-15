import numpy as np
import pickle

def pickle_vars(fileName, env, *variables):
    d = dict([(x, env[x]) for v in variables for x in env if v is env[x]])
    with open(fileName, 'wb') as f:
        pickle.dump(d, f)

# load the PDI data:
loaded_PDI = np.load("Output/pdi.npy")
PDI = loaded_PDI[1]	  # PDIs
PDI_years = loaded_PDI[0] # years

# load the SST data:
SST_MDR_OBS = np.load("Output/SST_MDR_OBS_hurricane_season.npy")
SST_MDR_OBS_years = np.load("Output/SST_MDR_OBS_hurricane_season_years.npy")

# load the RCP8.5 SST data:
SST_MDR_RCP85 = np.load("Output/SST_MDR_RCP85_hurricane_season.npy")
SST_MDR_RCP85_years = np.load("Output/SST_MDR_RCP85_hurricane_season_years.npy")

# adjust for different periods covered by PDI and SST data:
min_year=max(min(SST_MDR_OBS_years), min(PDI_years))
max_year=min(max(SST_MDR_OBS_years), max(PDI_years))
print("First and last years of SST and PDI data:"
      , SST_MDR_OBS_years[0], PDI_years[0], " and "
      , SST_MDR_OBS_years[-1], PDI_years[-1])
print("adjusted range where both have data:", min_year, max_year)
SST_MDR_OBS=SST_MDR_OBS[np.logical_and(SST_MDR_OBS_years>=min_year,
                                       SST_MDR_OBS_years<=max_year)]
SST_MDR_OBS_years=SST_MDR_OBS_years[np.logical_and(SST_MDR_OBS_years>=min_year
                                                   , SST_MDR_OBS_years<=max_year)]
PDI=PDI[np.logical_and(PDI_years>=min_year, PDI_years<=max_year)]
PDI_years=PDI_years[np.logical_and(PDI_years>=min_year, PDI_years<=max_year)]

hurricanes_number=np.load("Output/hurricanes_number.npy")
hurricanes_number_years=np.load("Output/hurricanes_number_years.npy")

HURSAT_wind_speed=np.load("Output/HURSAT_wind_speed.npy")
HURSAT_years=np.load("Output/HURSAT_years.npy")

pickle_vars('../code-for-students/hurricanes_variables.pickle', locals()
            ,PDI,PDI_years,SST_MDR_OBS,SST_MDR_OBS_years \
            ,SST_MDR_RCP85,SST_MDR_RCP85_years \
            ,hurricanes_number_years,hurricanes_number \
            ,HURSAT_wind_speed,HURSAT_years)

print("done.")
