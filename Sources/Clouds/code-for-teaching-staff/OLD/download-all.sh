echo 'https://www.earthsystemgrid.org/myopenid/eli.tziperman' > mypw
echo 'KRFY$Q5XrA70MNVbTYkg' >> mypw

./wget-hadgem-historical.sh -H -p < mypw
./wget-hadgem-rcp85.sh -H -p < mypw
./wget-gfdl-historical.sh -H -p < mypw
./wget-gfdl-rcp85.sh -H -p < mypw
./wget-hadgem-historical-clt.sh -H -p < mypw
./wget-hadgem-rcp85-clt.sh -H -p < mypw
./wget-gfdl-historical-clt.sh -H -p < mypw
./wget-gfdl-rcp85-clt.sh -H -p < mypw

