# Write a Python code to read a comma-separated text file
# "station-data.csv.gz", skipping the first line. Create a dictionary
# variable from the data with the keys taken from the second column
# and the values taken from the seventh column.

import csv
import gzip
import numpy as np
from datetime import datetime

def read_csv_file(file_path):
    data_dict = {}

    with gzip.open(file_path, 'rt') as file:
        reader = csv.reader(file)

        # Skip the header
        next(reader)
        
        for row in reader:
            if len(row) >= 7:  # Ensure the row has at least 7 columns
                key = row[1]    # name of station
                date = datetime.strptime(row[5], '%Y-%m-%d')   # date
                if row[6]=='':
                    value = np.nan
                else:
                    value = float(row[6])  # precipitation
                
                # Need to separate the first encounter of a key in
                # input file from following ones:
                if key in data_dict.keys():
                    data_dict[key][0].append(date)
                    data_dict[key][1].append(value)
                else:
                    data_dict[key]=[[],[]]
                    data_dict[key][0].append(date)
                    data_dict[key][1].append(value)


    return data_dict

# Main program:
file_path = '/Users/eli/Courses/EPS101/Data-for-teaching-staff/Floods/precipitation-station-data/station-data/station-data.csv.gz'
precipitation_station_data_dictionary = read_csv_file(file_path)

# save to npy file to be pickeled for students later:
np.save("Output/to-pickle/precipitation_station_data_dictionary.npy", precipitation_station_data_dictionary)
