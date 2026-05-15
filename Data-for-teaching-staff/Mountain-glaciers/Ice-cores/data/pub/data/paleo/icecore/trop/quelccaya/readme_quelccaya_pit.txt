Quelccaya Ice Cap Snow Pit Microparticle Data
-----------------------------------------------------------------------
               World Data Center for Paleoclimatology, Boulder
                                  and
                     NOAA Paleoclimatology Program
-----------------------------------------------------------------------
NOTE: Please cite original reference when using these data, 
plus the data file URL and date accessed.


NAME OF DATA SET: Quelccaya Ice Cap Snow Pit Microparticle Data
LAST UPDATE: 11/1990 (original recipt by WDC Paleo)  

CONTRIBUTOR: Thompson, L.G.


ORIGINAL REFERENCES:  
Thompson, L.G. (1980) Glaciological investigations of the tropical
Quelccaya Ice Cap, Peru. Journal of Glaciology, 25(91), p. 69-84.

Thompson, L.G., S. Hastenrath and B. Morales (1979) Climatic ice
core record from the tropical Quelccaya Ice Cap. Science,
203(4386), p. 1240-1243.



GEOGRAPHIC REGION: South America
PERIOD OF RECORD: 
FUNDING SOURCES: 


DESCRIPTION: 
List of files:

1. QUEL76.DAT - Quelccaya Ice Cap (QIC) 1976 field season samples: 
Coring was condu1cted in the bottom of the pits with a SIPRE coring
device.  These data represent the microparticle analyses of samples
from four sites on the ice cap.  Total samples in this file are
494.

  Site 1: The first 183 samples are from the summit of the QIC, 5650
meters, and represent sampling to a depth of 14.95 meters.

  Site 2: The next 161 samples are from the South Dome of the QIC
and represent sampling to a depth of 16.1 meters.

  Site 3: The next 140 samples are from the Middle Dome on the QIC
and represent sampling to a depth of 15.07 meters.

  Site 4: The next 10 samples are from the ablation zone on the QIC
and represent sampling to a depth of 1.37 meters.

2. QUEL77.DAT - Quelccaya Ice Cap 1977 field season samples:  Pits
were excavated and samples taken along the pit walls.  All pits
were at the summit.  Total samples are 85.

  Pit 1: 30 samples
  Pit 2: 31 samples
  Pit 3: 24 samples

3. QUEL78.DAT - Quelccaya Ice Cap 1978 samples from two shallow
pits.  These samples were processed twice on separate days.  Total
samples are 126.  These pits are from the summit of the QIC.

  Pit 1: 30 samples
  Pit 2: 33 samples
  Pit 3: 32 samples
  Pit 4: 31 samples



FILE FORMAT:

Record 1:
Columns  Format  Description
-------  ------  -----------
(01-06)    I6     Date of sample analysis
(07-10)    I4     Section number  
(11-13)    I3     Sample number
(14-21)    F8.3   Depth at the top of the sample (in meters)
(22-26)    F5.2   Size of the sample processed (in cm)
(27-32)    I6     Number of particles with diameters between 0.5-0.62
                  micrometers
(33-38)    I6     Number of particles with diameters between 0.63-0.79
                  micrometers
(39-44)    I6     Number of particles with diameters between 0.80-0.99
                  micrometers
(45-50)    I6     Number of particles with diameters between 1.0-1.24
                  micrometers
(51-56)    I6     Number of particles with diameters between 1.25-1.59
                  micrometers
(57-62)    I6     Number of particles with diameters between 1.6-1.99
                  micrometers
(63-68)    I6     Number of particles with diameters between 2.0-2.51
                  micrometers

Record 2:
Columns  Format  Description
-------  ------  -----------
(01-06)    I6     Number of particles with diameters between 2.52-3.16
                  micrometers
(07-12)    I6     Number of particles with diameters between 3.17-3.99
                  micrometers
(13-18)    I6     Number of particles with diameters between 4.0-4.99
                  micrometers
(19-24)    I6     Number of particles with diameters between 5.0-6.34
                  micrometers
(25-30)    I6     Number of particles with diameters between 6.35-7.99
                  micrometers
(31-36)    I6     Number of particles with diameters between 8.0-9.99
                  micrometers
(37-42)    I6     Number of particles with diameters between 10.0-
                  12.69 micrometers
(43-48)    I6     Number of particles with diameters between 12.7-16.0
                  micrometers
(49-54)    I6     Number of particles with diameters 0.5 micrometers
                  or larger
(55-60)    I6     Number of particles with diameters 0.63 micrometers
                  or larger
(61-66)    I6     Number of particles with diameters 0.80 micrometers
                  or larger
(67-72)    I6     Number of particles with diameters 1.0 micrometers
                  or larger

Record 3:
Columns  Format  Description
-------  ------  -----------
(01-06)    I6     Number of particles with diameters 1.25 micrometers
                  or larger
(07-12)    I6     Number of particles with diameters 1.6 micrometers
                  or larger
(13-18)    I6     Number of particles with diameters 2.0 micrometers
                  or larger
(19-24)    I6     Number of particles with diameters 2.52 micrometers
                  or larger
(25-30)    I6     Number of particles with diameters 3.17 micrometers
                  or larger
(31-36)    I6     Number of particles with diameters 4.0 micrometers
                  or larger
(37-42)    I6     Number of particles with diameters 5.0 micrometers
                  or larger
(43-48)    I6     Number of particles with diameters 6.35 micrometers
                  or larger
(49-54)    I6     Number of particles with diameters 8.0 micrometers
                  or larger
(55-60)    I6     Number of particles with diameters 10.0 micrometers
                  or larger
(61-66)    I6     Number of particles with diameters 12.7 micrometers
                  or larger
(67-71)    F5.1   Coarseness factor which equals the number of
                  particles with diameters 1.0 micrometers or larger,
                  divided by the total number with diameters 0.5
                  micrometers or larger.
(72)       I1     This factor has three possible values which
                  indicate the volume of sample analyzed by the
                  Coulter procedure.
                       (a)  if factor = 0 a 500 microliter sample was
                              processed,
                       (b)  if factor = 1 the sample is missing,
                       (c)  if factor = 2 a 50 microliter sample was
                              processed.