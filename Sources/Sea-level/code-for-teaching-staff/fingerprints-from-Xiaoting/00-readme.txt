Re: sea leve question
Yang, Xiaoting
Sep 9, 2020, 4:13 PM

Hi Eli,

   I created a folder called Sea_level_change in our shared folder for DEBC. In the Matlab folder, the data ready for direct use are called Greenland_melting.mat and Antarctica_melting.mat. In these files, 'lon_GL' is longitude, 'x_GL' is latitude, 'C' is the change in ice mask, and 'Delta_S' is the fingerprint corresponding to this mask change. The setup for this project is such that the ice mask has a uniform decrease of unit 1 (in variable 'C').

   If you want to reproduce these files, you can easily do so by running the MATLAB code called Final_main_script_Yang.m. All supporting files should be included in this folder. If you want a solution of higher resolution, change parameter 'maxdeg', to be any powers of two. On my laptop, maxdeg=128 takes a noticeably waiting time. The mat files we have now use maxdeg=128.

   Please let me know if you run into any problems using these files.

Best,
Xiaoting
