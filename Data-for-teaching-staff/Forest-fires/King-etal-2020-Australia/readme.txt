To make reading in the Jupyter notebook [analyze_Australia_fires_King_etal_2020.ipynb] easier, I manually added # at the start of headers and lines following the data in all four files. When doing this, I made sure that all months of the last un-commented year of data are available.

1) Rainfall monthly data (mm/month) averaged over the Murray-Darling Basin (Australia) were downloaded from the Bureau of Meteorology website:

http://www.bom.gov.au/cgi-bin/climate/change/timeseries.cgi?graph=rain&area=mdb&season=allmonths

2) Nino 3.4 (deg C) from
https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/nino34.long.data

3) dipole mode index (deg C, for Indian Ocean dipole):
https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data

4) Southern annular mode (SAM, related to amplitude of EOFs so nondim, although can be approximated by pressure difference at about 800 hPa between two latitudes):
data:
http://www.nerc-bas.ac.uk/public/icd/gjma/newsam.1957.2007.txt
overview:
https://atmos.colostate.edu/~davet/ao/Data/index.html
http://www.nerc-bas.ac.uk/icd/gjma/sam.html

The paper:

@article{King-Pitman-Henley-et-al-2020:role,
  title =	 {The role of climate variability in Australian
                  drought},
  author =	 {King, Andrew D and Pitman, Andy J and Henley,
                  Benjamin J and Ukkola, Anna M and Brown, Josephine
                  R},
  journal =	 {Nature Climate Change},
  volume =	 10,
  number =	 3,
  pages =	 {177--179},
  year =	 2020,
  publisher =	 {Nature Publishing Group}
}

