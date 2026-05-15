From Ian, these data add ice cover to close the unobserved hole at the north pole, which is present in the sea ice area indices from NSIDC but perhaps not in the extent index. The reference, according to Ian, is:

@article{Fetterer-Knowles-Meier-et-al-2017:sea,
  Author =	 {F. Fetterer and K. Knowles and W. Meier and M.
                  Savoie and A. Windnagel},
  Journal =	 {Natl. Snow and Ice Data Cent., Boulder, Colo.},
  Note =	 {Updated daily. http://nsidc.org/data/g02135.html},
  Title =	 {Sea ice index, Version 3},
  Year =	 2017
}


From: Ian Eisenman
Date: Oct 16, 2020, 8:20 PM
To: me

Hi Eli,

Thanks for your email. I'm glad to hear that my comments were useful!

Regarding the question you wrote in red, according to my notes, the area of the Arctic pole hole is 1.19 during 10/1978-6/1987, 0.31 during 7/1987-12/2007, and 0.029 during 1/2008-present (all in units of million km^2). My notes for this are based just on the ice area and ice extent values reported in the "NSIDC sea ice index" dataset, which leaves the pole hole as zero for ice area but fills it with ice for ice extent. Note that in the "Bootstrap" dataset, ice area and ice extent values distributed by NSIDC, the pole hole is filled with ice for both ice area and ice extent.

I'm attaching text files that I created with NSIDC sea ice index values. I don't think this is the *best* dataset or anything like that, but it's a popular one, and it's usually my go-to sea ice cover dataset. I figured it could perhaps be useful here just to make sure it gives similar values to what you have. The NSIDC sea ice index dataset is based on the NASA Team algorithm, which is probably what you're using too, based on the filenames you mentioned. So, I expect that my data should be very similar to yours. For the data in the attached text files, I downloaded monthly ice area and ice extent values from https://nsidc.org/data/seaice_index/archives and filled the pole hole for ice area as described above. I also addressed NaN values in 12/1987 & 1/1988 (the SSM/I instrument was turned off for much of December 1987 and January 1988 due to overheating issues): I filled these values by linearly interpolating between the same month in the previous year and the following year. My two text files should be pretty self-explanatory, just listing year, month, and ice area or ice extent. For example, if you're using Matlab, you could just enter these commands:
    M=dlmread('SeaIceIndex_NH_area.txt'); % load ice area data
    disp(M(M(:,1)==1979 & M(:,2)==9,3)) % 9/1979 value
    disp(M(M(:,1)==2012 & M(:,2)==9,3)) % 9/2012 value
    t=M(:,1)+(M(:,2)-0.5)/12; % time in yrs
    x=M(:,3); % ice area
    plot(t,x)

