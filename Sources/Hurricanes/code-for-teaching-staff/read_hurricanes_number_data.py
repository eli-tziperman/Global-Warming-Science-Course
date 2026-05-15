import numpy as np
import pandas as pd

data_dir='../../../Data-for-teaching-staff/Hurricanes/'
data_file='vk_11_hurricane_counts.txt'
dataset = pd.read_csv(data_dir+data_file,na_values='NaN'
    ,sep=r"\s+",comment='#',skipinitialspace=True
                      ,skip_blank_lines=True,header=0)
data = np.asarray(dataset.iloc[:, :].values)
##header = dataset.iloc[:, :].columns
hurricanes_number_years=1.0*data[:,0]
hurricanes_number=1.0*data[:,1]

# save for use in Hurricanes module workshop:
np.save("Output/hurricanes_number_years",hurricanes_number_years)
np.save("Output/hurricanes_number",hurricanes_number)

print("Done reading data, saved npy files to be picked into Output/.")
