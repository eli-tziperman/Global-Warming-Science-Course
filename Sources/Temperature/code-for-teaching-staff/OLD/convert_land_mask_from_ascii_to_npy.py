"""
This script converts the 180x360 ASCII land percentage (water_percent_1d.asc)
mask from
https://web.archive.org/web/20060831045533/http://islscp2.sesda.com/ISLSCP2_1/data/ancillary/land_water_masks_xdeg/land_water_masks_xdeg.zip
into a 90x180 array of booleans, exported as a .npy file

Creates file:
    land_mask.npy
    2D Array of bools. Accessed via [lat, lon]. True represents land,
        False represents water.

To use, ensure that the variable MASK_PATH directly below this __doc__ 
string contains a valid path to the .asc file, then run. land_mask.npy
will be created in ./Output/

Yonathan Vardi 2019-07-16
"""
########################################################################
MASK_PATH = "../../../Data-for-teaching-staff/Temperature/water_percent_1d.asc"
########################################################################

import numpy as np

#open the file containing the mask
mask_file = open(MASK_PATH, "r")
#read the contents from it, then close the file
text_mask = mask_file.read()
mask_file.close()

# convert it to a 2D array of ints
lines = text_mask.splitlines()
values = []
for i in lines:
    values.append(np.asarray(list(map(int, i.split()))))
values = np.asarray(values)

#To fit with the data it will be masking, half both its dimensions
half_values = []
for i in range(0, len(values), 2):
    half_values.append([])
    for j in range(0, len(values[0]), 2):
        # set each point on the downsized array to be the average of 
        # the four points that are compressed into it
        # print(i, j, values.shape, len(half_values))
        half_values[i//2].append((values[i,j] + values[i+1,j] + values[i,j+1]
                               + values[i+1,j+1])/4)
    half_values[i//2] = np.asarray(half_values[i//2])
half_values = np.asarray(half_values)
#and flip it
half_values = np.flip(half_values, axis=0)

# get a true/false for all values on whether they are >= 50
# this is the land mask.
mask = half_values >= 50

np.save("./Output/land_mask.npy", mask)
