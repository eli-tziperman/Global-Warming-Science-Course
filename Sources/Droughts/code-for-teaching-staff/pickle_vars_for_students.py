import numpy as np
import pickle
import os


print("pickling variables for students:")
# location of input npy files:
path_to_npy_files='Output/'
# desired location of output pickle file:
pickle_file_name='../code-for-students/droughts_variables.pickle'
# remove pickle file if already exists
if os.path.exists(pickle_file_name):
    os.remove(pickle_file_name)

# sort file names from output folder:
filelist=os.listdir(path_to_npy_files)
filelist.sort()

# read data that could not be saved as npy
with open('Output/all_individual_tree_records.pickle', 'rb') as file:
    data1 = pickle.load(file)
    all_individual_tree_records_years = data1['all_individual_tree_records_years']
    all_individual_tree_records_widths = data1['all_individual_tree_records_widths']

mydict = {}
# open pickle file and add one variable at a time:
with open(pickle_file_name, 'wb') as pickfile:
    for filename in filelist:
        # load and pickle the data from .npy files only:
        if '.npy' in filename:
            print("loading and pickling ",path_to_npy_files+filename)
            data=np.load(path_to_npy_files+filename,allow_pickle=True);
            # remove file extension to get variable name:
            varname=filename.replace(".npy","")
            # add to the dictionary:
            mydict[varname] = data
        # add tree ring data that could not be saved as npy and was pickled instead:
        mydict["all_individual_tree_records_widths"] = all_individual_tree_records_widths
        mydict["all_individual_tree_records_years"] = all_individual_tree_records_years
    # and save it to the pickle file:
    pickle.dump(mydict, pickfile, protocol=pickle.HIGHEST_PROTOCOL)
