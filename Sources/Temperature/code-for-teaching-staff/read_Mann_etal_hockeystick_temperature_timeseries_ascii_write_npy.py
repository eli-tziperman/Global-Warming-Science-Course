"""
Extract the "hockey stick" data from Mann et al into a .npy file.

data from the bottom of
http://www.meteo.psu.edu/holocene/public_html/supplements/MultiproxyMeans07/
http://www.meteo.psu.edu/holocene/public_html/supplements/MultiproxyMeans07/glglhadfulsm20
(labeled as the "data for the blue line" in the section of this webpage where the
effects of the seven potential problematic proxies are discussed.)

Sample of file format:
    ;comments (not in original file)
        5.0100000e+02  -3.4786136e-01
        5.0200000e+02  -3.3935701e-01
        5.0300000e+02  -3.2940641e-01

    columns are (years, data)

original version: Yonathan Vardi 2019-07-11; revised: Eli, 202512
"""
import numpy as np
import matplotlib.pyplot as plt

# Path to the data file:
filename_input = "../../../Data-for-teaching-staff/Temperature/mann_et_al.txt"

# read data:
years, anomalies = np.loadtxt(filename_input, comments=';', unpack=True)
float_array_2D = np.column_stack((years, anomalies))

# save to npy:
filename_output = "./Output/to-pickle/hockeystick_annual_temperature_anomaly_timeseries.npy"
np.save(filename_output, float_array_2D)

# load the file and plot it to verify the validity of the data
f = np.load(filename_output, allow_pickle=True)
plt.plot(f[:,0], f[:,1])
plt.grid()
plt.title("hocky stick")
plt.ylabel("Degrees C"); plt.xlabel("Years")
plt.savefig("Output/Figures/temperature-hockeystick.pdf",format='pdf');
plt.show()
