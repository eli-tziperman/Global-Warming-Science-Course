import numpy as np
from numpy import linalg
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd

# font required by PUP:
plt.rcParams['font.family'] = 'Myriad Pro'

data=np.asarray(pd.read_table("../../../Data-for-teaching-staff/Sea-level/Jevrejeva_etal_2008.txt",skiprows=14,sep='\\s+'))

fig=plt.figure(figsize=(5,3.5))
plt.plot(data[:,0],data[:,1]/10,color=[0,0,1])
plt.fill_between(data[:,0],data[:,1]/10-data[:,2]/10,data[:,1]/10+data[:,2]/10,lw=0.1,color=[0,0.75,1])
plt.xlabel("year")
plt.ylabel("GMSL (cm)")
plt.grid(lw=0.25)
plt.tight_layout()
# saved in workshop solutions.
plt.show()
