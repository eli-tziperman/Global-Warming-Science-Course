#!/bin/bash
# script to get the numbers for the heat trend detection & attribution
id=ec8907341dfc63c526d08e36d06b7ed8
echo "annual mean Austrlia-wide temperature, GISTEMP"
if [ ! -s fit_annual_australia.html ]; then
curl https://climexp.knmi.nl/get_index.cgi\?email=$id\&field=giss_temp_250\&gridpoints=false\&intertype=nearest\&lat1=-45\&lat2=-10\&lon1=110\&lon2=155\&maskmetadata=data/maskAustralia.$id.poly\&masktype=5lan\&minfac=30\&standardunits=standardunits > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NAME=mean\&NPERYEAR=12\&STATION=GISS_250_T2m/SST_anom_Australia_5lan\&TYPE=i\&WMO=giss_temp_250_Australia_5lan_su\&assume=shift\&begin=1910\&begin2=1900\&ci=95\&dgt=80\&fit=gauss\&minfac=30\&month=1\&nbin=20\&operation=averaging\&prog=mean\&restrain=0\&sum=12\&timeseries=gmst\&type=attribute\&year=2019 > fit_annual_australia.html
fi
fgrep 'alpha;:' fit_annual_australia.html

echo "annual T2m bush fire region, GISTEMP"
if [ ! -s fit_annual_t2m.html ]; then
curl https://climexp.knmi.nl/get_index.cgi\?email=$id\&field=giss_temp_250\&gridpoints=false\&intertype=nearest\&lat1=-45\&lat2=-10\&lon1=110\&lon2=155\&maskmetadata=data/mask0.$id.poly\&masktype=5lan\&minfac=30\&standardunits=standardunits > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=12\&STATION=GISS250_bushfire\&TYPE=i\&WMO=giss_temp_250_mask0_5lan_su\&assume=shift\&begin=1910\&begin2=1900\&ci=95\&dgt=80\&fit=gauss\&minfac=30\&month=1\&nbin=20\&operation=averaging\&restrain=0\&sum=12\&timeseries=gmst\&type=attribute\&year=2019 > fit_annual_t2m.html
fi
fgrep 'alpha;:' fit_annual_t2m.html

echo "annual T2m bush fire region, Berkeley"
if [ ! -s fit_annual_t2m_berkeley.html ]; then
curl https://climexp.knmi.nl/get_index.cgi?email=$id\&field=giss_temp_250\&gridpoints=false\&intertype=nearest\&lat1=-45\&lat2=-10\&lon1=110\&lon2=155\&maskmetadata=data/mask0.$id.poly\&masktype=5lan\&minfac=30\&standardunits=standardunits > /dev/null
curl https://climexp.knmi.nl/attribute.cgi?EMAIL=$id\&NPERYEAR=12\&STATION=t2m_Berkeley_bushfire\&TYPE=i\&WMO=berkeley_tavg_mask0_5lan_su_ext\&assume=shift\&begin=1910\&begin2=1900\&ci=95\&dgt=80\&fit=gauss\&minfac=30\&month=1\&nbin=20\&operation=averaging\&restrain=0\&sum=12\&timeseries=gmst\&type=attribute\&year=2019 > fit_annual_t2m_berkeley.html
fi
fgrep 'alpha;:' fit_annual_t2m_berkeley.html

echo "DJF Tmax bush fire region, Berkeley, DJF2020 arbitrary"
if [ ! -s fit_DJF_tmax_berkeley.html ]; then
curl https://climexp.knmi.nl/getindices.cgi?STATION=t2m_Berkeley_bushfire\&TYPE=i\&WMO=SEAustralia/berkeley_tavg_mask0_5lan_su_ext\&id=$id > /dev/null
curl https://climexp.knmi.nl/attribute.cgi?EMAIL=$id\&NPERYEAR=12\&STATION=t2m_Berkeley_bushfire\&TYPE=i\&WMO=berkeley_tavg_mask0_5lan_su_ext\&assume=shift\&begin=1910\&begin2=1900\&ci=95\&dgt=80\&fit=gauss\&minfac=30\&month=12\&nbin=20\&operation=averaging\&restrain=0\&sum=3\&timeseries=gmst\&type=attribute\&xyear=3.5\&year=2019 > fit_DJF_tmax_berkeley.html
fi
fgrep 'alpha;:' fit_DJF_tmax_berkeley.html

echo "DJF max 7-day Tmax bush fire region, Berkeley"
if [ ! -s fit_max7_DJF_tmax_berkeley.html ]; then
curl http://climexp.knmi.nl/get_index.cgi?email=$id\&field=data/TMAX_Daily_LatLong1_full_110-155E_-45--10N_su_extended.info_4_max_7v.$id.info\&gridpoints=false\&intertype=nearest\&lat1=-40\&lat2=-10\&lon1=110\&lon2=155\&maskmetadata=data/mask0.$id.poly\&minfac=30\&standardunits=standardunits > /dev/null
curl https://climexp.knmi.nl/attribute.cgi?EMAIL=$id\&NPERYEAR=4\&STATION=seasonal_maximum_of_7-daily_Air_Surface_Temperature\&TYPE=i\&WMO=TMAX_Daily_LatLong1_full_110-155E_-45--10N_su_extended.info_4_max_7v_mask0_su\&assume=shift\&begin=1910\&begin2=1900\&ci=95\&dgt=80\&fit=gev\&minfac=30\&month=1\&nbin=20\&operation=averaging\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_berkeley.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_berkeley.html
fgrep 'probability ratio' fit_max7_DJF_tmax_berkeley.html
fgrep 'return values<' fit_max7_DJF_tmax_berkeley.html

echo "DJF max 7-day Tmax bush fire region, Berkeley, 2019 included in fit"
if [ ! -s fit_max7_DJF_tmax_berkeley_included.html ]; then
curl https://climexp.knmi.nl/attribute.cgi?EMAIL=$id\&NPERYEAR=4\&STATION=seasonal_maximum_of_7-daily_Air_Surface_Temperature\&TYPE=i\&WMO=TMAX_Daily_LatLong1_full_110-155E_-45--10N_su_extended.info_4_max_7v_mask0_su\&assume=shift\&begin=1910\&begin2=1900\&ci=95\&dgt=80\&fit=gev\&minfac=30\&month=1\&nbin=20\&operation=averaging\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019\&includelast=on > fit_max7_DJF_tmax_berkeley_included.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_berkeley_included.html
fgrep 'probability ratio' fit_max7_DJF_tmax_berkeley_included.html
fgrep 'return values<' fit_max7_DJF_tmax_berkeley_included.html

echo "DJF max 7-day Tmax bush fire region, ACORN stations, 2019 read off from scatter plot"
if [ ! -s fit_max7_DJF_tmax_acorn.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/tmax_acorn_ave\&STATION=ACORN_stations_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=ACORN_stations_Tmax\&TYPE=i\&WMO=tmax_acorn_ave\&amoeba=on\&assume=shift\&begin=1910\&begin2=1900\&blockyr=1\&ci=95\&dgt=80\&fit=gev\&includelast=on\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&xyear=35.6\&year=2019 > fit_max7_DJF_tmax_acorn.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_acorn.html
fgrep 'probability ratio' fit_max7_DJF_tmax_acorn.html
fgrep 'return values<' fit_max7_DJF_tmax_acorn.html

echo "DJF max 7-day Tmax bush fire region, AWAP, 2019 included in fit"
if [ ! -s fit_max7_DJF_tmax_awap.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/awap_tmax_-1_max_50_7v_mask0_5lan_su\&STATION=AWAP_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=AWAP_Tmax\&TYPE=i\&WMO=awap_tmax_-1_max_50_7v_mask0_5lan_su\&amoeba=on\&assume=shift\&begin=1910\&begin2=1900\&blockyr=1\&ci=95\&dgt=80\&fit=gev\&includelast=on\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_awap.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_awap.html
fgrep 'probability ratio' fit_max7_DJF_tmax_awap.html
fgrep 'return values<' fit_max7_DJF_tmax_awap.html

echo "DJF max 7-day Tmax bush fire region, 20CRv3, 10-yr RT"
if [ ! -s fit_max7_DJF_tmax_20crv3.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/c3tmax_daily_-1_max_50_7v_trend_mask47_land_su\&STATION=20CRv3_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=20CRv3_Tmax\&TYPE=i\&WMO=c3tmax_daily_-1_max_50_7v_trend_mask47_land_su\&amoeba=on\&anomal=on\&assume=shift\&begin=1910\&begin2=1900\&biasrt=10\&blockyr=1\&ci=95\&dgt=80\&fit=gev\&includelast=on\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_20crv3.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_20crv3.html
fgrep 'probability ratio' fit_max7_DJF_tmax_20crv3.html
fgrep 'return values<' fit_max7_DJF_tmax_20crv3.html

echo "DJF max 7-day Tmax bush fire region, CERA-20C, 10-yr RT"
if [ ! -s fit_max7_DJF_tmax_cera20c.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/CERA20C_DJF_TX7x_region_@@\&STATION=CERA-20C_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=CERA-20C_Tmax\&TYPE=i\&WMO=CERA20C_DJF_TX7x_region_@@\&amoeba=on\&anomal=on\&assume=shift\&begin=1910\&begin2=1900\&biasrt=10\&blockens=1\&blockyr=1\&ci=95\&dgt=80\&end=2009\&fit=gev\&includelast=on\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_cera20c.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_cera20c.html
fgrep 'probability ratio' fit_max7_DJF_tmax_cera20c.html
fgrep 'return values<' fit_max7_DJF_tmax_cera20c.html

echo "DJF max 7-day Tmax bush fire region, JRA55"
if [ ! -s fit_max7_DJF_tmax_jra55.html ]; then
curl http://climexp.knmi.nl/getindices.cgi?WMO=SEAustralia/JRA55_TX7x_DJF_NSW\&STATION=tmax_JRA55_bushfire\&TYPE=i\&id=$id > /dev/null
curl http://climexp.knmi.nl/attribute.cgi?EMAIL=$id\&NPERYEAR=1\&STATION=tmax_JRA55_bushfire\&TYPE=i\&WMO=JRA55_TX7x_DJF_NSW\&amoeba=on\&assume=shift\&begin2=1900\&biasrt=10\&blockyr=1\&ci=95\&dgt=80\&end=2019\&fit=gev\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019\&anomal=on > fit_max7_DJF_tmax_jra55.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_berkeley.html
fgrep 'probability ratio' fit_max7_DJF_tmax_berkeley.html
fgrep 'return values<' fit_max7_DJF_tmax_berkeley.html

echo "DJF max 7-day Tmax bush fire region, EC-Earth T159"
if [ ! -s fit_max7_DJF_tmax_ecearth.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?NPERYEAR=4\&TYPE=i\&WMO=SEAustralia/tasmax_day_ECEARTH23_rcp85___110-155E_-45--10N_su_info_4_max_7v_mask0_land_su_%%\&id=$id > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=4\&STATION=seasonal_maximum_of_7-daily_Daily_Maximum_Near-Surface_Air_Temperature\&TYPE=i\&WMO=tasmax_day_ECEARTH23_rcp85___110-155E_-45--10N_su_info_4_max_7v_mask0_land_su_%%\&assume=shift\&begin2=1900\&biasrt=10\&ci=95\&dgt=80\&end=2019\&fit=gev\&month=1\&nbin=20\&operation=averaging\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_ecearth.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_ecearth.html
fgrep 'probability ratio' fit_max7_DJF_tmax_ecearth.html
fgrep 'return values<' fit_max7_DJF_tmax_ecearth.html

echo "DJF max 7-day Tmax bush fire region, HadGEM3-A N219"
if [ ! -s fit_max7_DJF_tmax_hadgem3a.html ]; then
curl https://climexp.knmi.nl/get_index.cgi\?email=$id\&field=data/tasmax_day_HadGEM3-A-N216_historical_110-155E_-45--10N_su.info_4_max_7v_%%%.$id.info\&gridpoints=false\&intertype=nearest\&lat1=-45\&lat2=-10\&lon1=110\&lon2=155\&maskmetadata=data/mask0.$id.poly\&masktype=land\&standardunits=standardunits > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=4\&STATION=seasonal_maximum_of_7-daily_Daily_Maximum_Near-Surface_Air_Temperature\&TYPE=i\&WMO=tasmax_day_HadGEM3-A-N216_historical_110-155E_-45--10N_su_info_4_max_7v_____mask0_land_su_%%%\&assume=shift\&begin2=1900\&ci=95\&dgt=80\&fit=gev\&month=1\&nbin=20\&operation=averaging\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&xyear=38\&year=2019 > fit_max7_DJF_tmax_hadgem3a.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_hadgem3a.html
fgrep 'probability ratio' fit_max7_DJF_tmax_hadgem3a.html
fgrep 'return values<' fit_max7_DJF_tmax_hadgem3a.html

echo "DJF max 7-day Tmax bush fire region, GFDL-ESM2M"
if [ ! -s fit_max7_DJF_tmax_gfdl-esm2m.html ]; then
curl http://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/GFDL-ESM2M_1950-2100_SONDJF_max_tasmax_7day_runmean_@@\&STATION=GFDL-ESM2M_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl http://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=GFDL-ESM2M_Tmax\&TYPE=i\&WMO=GFDL-ESM2M_1950-2100_SONDJF_max_tasmax_7day_runmean_@@\&anomal=on\&assume=shift\&begin2=1900\&biasrt=10\&ci=95\&dgt=80\&end=2019\&fit=gev\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_gfdl-esm2m.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_gfdl-esm2m.html
fgrep 'probability ratio' fit_max7_DJF_tmax_gfdl-esm2m.html
fgrep 'return values<' fit_max7_DJF_tmax_gfdl-esm2m.html

echo "DJF max 7-day Tmax bush fire region, CESM1-CAM5"
if [ ! -s fit_max7_DJF_tmax_cesm1-cam5.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/CESM1-CAM5_1920-2100_SONDJF_max_tasmax_7day_runmean_@@\&STATION=CESM1-CAM5_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=CESM1-CAM5_Tmax\&TYPE=i\&WMO=CESM1-CAM5_1920-2100_SONDJF_max_tasmax_7day_runmean_@@\&anomal=on\&assume=shift\&begin2=1900\&biasrt=10\&ci=95\&dgt=80\&end=2019\&fit=gev\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_cesm1-cam5.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_cesm1-cam5.html
fgrep 'probability ratio' fit_max7_DJF_tmax_cesm1-cam5.html
fgrep 'return values<' fit_max7_DJF_tmax_cesm1-cam5.html

echo "DJF max 7-day Tmax bush fire region, CanESM2"
if [ ! -s fit_max7_DJF_tmax_canesm2.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/CanESM2_1950-2100_DJF_max_tasmax_7day_runmean_@@\&STATION=CanESM2_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=CanESM2_Tmax\&TYPE=i\&WMO=CanESM2_1950-2100_DJF_max_tasmax_7day_runmean_@@\&anomal=on\&assume=shift\&begin2=1900\&biasrt=10\&ci=95\&dgt=80\&end=2019\&fit=gev\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_canesm2.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_canesm2.html
fgrep 'probability ratio' fit_max7_DJF_tmax_canesm2.html
fgrep 'return values<' fit_max7_DJF_tmax_canesm2.html

echo "Model evaluation: scale parameter sigma"
fgrep sigma fit_max7_DJF_tmax*html | fgrep 1900
echo "Model evaluation: shape parameter xi"
fgrep '&xi;:' fit_max7_DJF_tmax*html

echo "Jul-Jun max 7-day Tmax bush fire region, IPSL-CM6"
if [ ! -s fit_max7_DJF_tmax_ipsl-cm6.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/ipsl_yearly_tmax_july-june_nsw_@@\&STATION=IPSL_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=IPSL_Tmax\&TYPE=i\&WMO=ipsl_yearly_tmax_july-june_nsw_@@\&assume=shift\&begin2=1900\&biasrt=10\&ci=95\&dgt=80\&end=2019\&fit=gev\&month=1\&nbin=20\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_ipsl-cm6.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_ipsl-cm6.html
fgrep 'probability ratio' fit_max7_DJF_tmax_ipsl-cm6.html
fgrep 'return values<' fit_max7_DJF_tmax_ipsl-cm6.html

echo "Jul-Jun max 7-day Tmax bush fire region, asf20c_1901 1901-2010"
if [ ! -s fit_max7_DJF_tmax_asf20c_1901.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/asf20c_1901_TX7x_DJF_1900_2009_NSW_@@\&STATION=ASF20C_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl http://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=asf20c_1901_Tmax\&TYPE=i\&WMO=ASF20C_TX7x_DJF_1900_2009_NSW_@@\&amoeba=on\&assume=shift\&begin2=1900\&biasrt=10\&blockens=1\&blockyr=1\&ci=95\&dgt=80\&begin=1901\&end=2019\&fit=gev\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019\&anomal=on > fit_max7_DJF_tmax_asf20c_1901.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_asf20c_1901.html
fgrep 'probability ratio' fit_max7_DJF_tmax_asf20c_1901.html
fgrep 'return values<' fit_max7_DJF_tmax_asf20c_1901.html

echo "Jul-Jun max 7-day Tmax bush fire region, ASF20C 1960-2010"
if [ ! -s fit_max7_DJF_tmax_asf20c.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/ASF20C_TX7x_DJF_1900_2009_NSW_@@\&STATION=ASF20C_Tmax\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl http://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=ASF20C_Tmax\&TYPE=i\&WMO=ASF20C_TX7x_DJF_1900_2009_NSW_@@\&amoeba=on\&assume=shift\&begin2=1900\&biasrt=10\&blockens=1\&blockyr=1\&ci=95\&dgt=80\&begin=1960\&end=2019\&fit=gev\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019\&anomal=on > fit_max7_DJF_tmax_asf20c.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_asf20c.html
fgrep 'probability ratio' fit_max7_DJF_tmax_asf20c.html
fgrep 'return values<' fit_max7_DJF_tmax_asf20c.html

echo "Jul-Def max 7-day Tmax bush fire region, weather@home actual"
if [ ! -s fit_max7_DJF_tmax_w@h_actual.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/wah_yearly_tmax_seasmax_nsw_actual_@@\&STATION=W@H_Tmax_actual\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=W@H_Tmax_actual\&TYPE=i\&WMO=wah_yearly_tmax_seasmax_nsw_actual_@@\&amoeba=on\&assume=shift\&begin=1910\&begin2=1900\&biasrt=10\&blockens=1\&blockyr=1\&ci=95\&dgt=80\&fit=gev\&includelast=on\&month=1\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_w@h_actual.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_w@h_actual.html
fgrep 'probability ratio' fit_max7_DJF_tmax_w@h_actual.html
fgrep 'return values<' fit_max7_DJF_tmax_w@h_actual.html

echo "Jul-Def max 7-day Tmax bush fire region, weather@home natural"
if [ ! -s fit_max7_DJF_tmax_w@h_natural.html ]; then
curl https://climexp.knmi.nl/getindices.cgi\?WMO=SEAustralia/wah_yearly_tmax_seasmax_nsw_natural_@@\&STATION=W@H_Tmax_natural\&TYPE=i\&id=$id\&NPERYEAR=1 > /dev/null
curl https://climexp.knmi.nl/attribute.cgi\?EMAIL=$id\&NPERYEAR=1\&STATION=W@H_Tmax_natural\&TYPE=i\&WMO=wah_yearly_tmax_seasmax_nsw_natural_@@\&amoeba=on\&assume=shift\&begin2=1900\&biasrt=10\&blockens=1\&blockyr=1\&ci=95\&dgt=80\&fit=gev\&month=1\&nbin=20\&restrain=0\&sum=1\&timeseries=gmst\&type=attribute\&year=2019 > fit_max7_DJF_tmax_w@h_natural.html
fi
fgrep 'alpha;:' fit_max7_DJF_tmax_w@h_natural.html
fgrep 'probability ratio' fit_max7_DJF_tmax_w@h_natural.html
fgrep 'return values<' fit_max7_DJF_tmax_w@h_natural.html

echo "Model evaluation: scale parameter sigma"
fgrep '&sigma;' fit_max7_*.html  | fgrep 1900 | sed -e 's@:.*1900</td><td> *@: @' -e 's@</td><td> *@ @' -e 's@\.\.\. *@ @' -e 's@</td></tr>@@'
echo "Model evaluation: shape parameter xi"
fgrep '&xi;:' fit_max7_*.html  | sed -e 's@:.*&xi;:</td><td>          @ @' -e 's@</td><td>         @@' -e 's@...         @@' -e 's@</td></tr>@@'

echo "Attribution: PR"
fgrep 'atra' fit_max7_*.html | sed -e 's@:.*&nbsp;</td><td> *@ @' -e 's@</td><td> *@ @' -e 's@ *\.\.\. *@ @' -e 's@</td></tr>@@' | sed -e 's/&infin;/1e6/g'
echo "Attribution: ∆T"
fgrep 'return values<' fit_max7_*.html | sed -e 's@:.*diff</td><td> *@ @' -e 's@</td><td> *@ @' -e 's@ *\.\.\. *@ @' -e 's@</td></tr>@@' | sed -e 's/&infin;/1e6/g'
