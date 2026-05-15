#!/bin/sh
# run all codes for teaching staff to produce data and images for students.

# echo commands to screen:
set -o verbose
# Any subsequent commands which fail will cause the shell script to
# exit immediately:
set -e

#cd ~/Dropbox/Courses/EPS101/Sources/Clouds/code-for-teaching-staff/

\rm -rf Output/to-pickle/*.npy
python process_GCM_data_for_Clouds_chapter_cloud.py
python pickle_vars_for_students.py
