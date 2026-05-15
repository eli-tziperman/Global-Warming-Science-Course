import numpy as np
from numpy import genfromtxt
import pickle

def pickle_vars(fileName, env, *variables):
    d = dict([(x, env[x]) for v in variables for x in env if v is env[x]])
    with open(fileName, 'wb') as f:
        pickle.dump(d, f)

# files to be pickled created by prepare-figures-for-introduction.ipynb:
directory="Output/to-pickle/" 
T = np.load("Output/to-pickle/Temperature.npy").T
CO2 = np.load("../../Greenhouse/code-for-teaching-staff/Output/to-pickle/CO2_observed.npy")
CO2_years = np.load("../../Greenhouse/code-for-teaching-staff/Output/to-pickle/CO2_observed_years.npy")
CO2=np.stack([CO2_years,CO2]).T
print(CO2.shape)

pickle_vars('../code-for-students/introduction_python_variables.pickle', locals()\
            ,T,CO2)
