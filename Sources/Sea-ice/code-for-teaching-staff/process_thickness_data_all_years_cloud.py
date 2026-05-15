import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os, re, io, gzip
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # silence verify=False warning
import xarray as xr

BASE="https://pscfiles.apl.uw.edu/zhang/PIOMAS/data/v2.1/heff/"
PAT=re.compile(r"heff\.H(\d{4})\.nc\.gz")

VERIFY=False
ENGINE="scipy"
get=lambda url,timeout=120: requests.get(url, verify=VERIFY, timeout=timeout)
open_year=lambda y: xr.open_dataset(
    io.BytesIO(gzip.decompress(get(f"{BASE}heff.H{y}.nc.gz").content)),
    engine=ENGINE
)

years=sorted({int(y) for y in PAT.findall(get(BASE,timeout=60).text)})
if not years: raise SystemExit("No heff.HYYYY.nc.gz links found at "+BASE)

# if the last available file is incomplete (<12 months), drop it
ds=open_year(years[-1])
if ds['heff'].sizes.get('n', ds['heff'].shape[0]) < 12: years=years[:-1]
ds.close()
first_year_thickness, last_year_thickness = years[0], years[-1]
print("Found thickness data for the year range:", first_year_thickness, last_year_thickness)

os.makedirs("Output/thickness_npy", exist_ok=True)
os.makedirs("Output/to-pickle", exist_ok=True)

sic_thickness_obs_lon = sic_thickness_obs_lat = sic_thickness_cell_area = None

for year in years:
    print(year)
    ds=open_year(year)

    v=ds["heff"].where(ds["heff"]<5000) # missing value is 9999.9
    A=v.transpose("j","i","n").values[:, :, :12]
    np.save(f"Output/thickness_npy/sic_thickness_obs{year}.npy", A)

    if sic_thickness_obs_lon is None:
        sic_thickness_obs_lon = ds["lon_scaler"].values
        sic_thickness_obs_lat = ds["lat_scaler"].values
        sic_thickness_cell_area = (ds["dxt"].values*ds["dyt"].values) \
            if ("dxt" in ds and "dyt" in ds) else np.ones_like(sic_thickness_obs_lon)

        np.save("Output/to-pickle/sic_thickness_obs_lon.npy", sic_thickness_obs_lon)
        np.save("Output/to-pickle/sic_thickness_obs_lat.npy", sic_thickness_obs_lat)
        np.save("Output/to-pickle/sic_thickness_obs_cell_area.npy", sic_thickness_cell_area)

    ds.close()

# plot:
# -----
plt.figure(figsize=(6,6))
sic_thickness_obs_first_year=np.load("Output/thickness_npy/sic_thickness_obs"
                                     +repr(first_year_thickness)+".npy")
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0, globe=None))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
c=plt.pcolormesh(sic_thickness_obs_lon, sic_thickness_obs_lat
                 , sic_thickness_obs_first_year[:,:,3] \
                 ,transform=ccrs.PlateCarree(), cmap='jet',shading='auto')
plt.xticks(np.arange(-60,0,20))
plt.yticks(np.arange(50,90,10))
plt.title('sea ice sic_thickness_obs '+repr(first_year_thickness));
plt.colorbar(c, shrink=0.7, pad=0.02)
plt.pause(2)

f=plt.gcf()
f.set_size_inches(5,4)
f.savefig("Output/Figure-sea-ice-thickness-"+repr(first_year_thickness)+".pdf", format="pdf")

plt.clf()
plt.figure(figsize=(6,6))
sic_thickness_obs_last_year=np.load("Output/thickness_npy/sic_thickness_obs"
                                     +repr(last_year_thickness)+".npy")
ax = plt.axes(projection=ccrs.NorthPolarStereo(central_longitude=0.0, globe=None))
ax.set_extent([0, 359.999, 55, 90], crs=ccrs.PlateCarree())
ax.coastlines(resolution='110m')
ax.gridlines()
c=plt.pcolormesh(sic_thickness_obs_lon, sic_thickness_obs_lat
                 , sic_thickness_obs_last_year[:,:,3]\
                 , transform=ccrs.PlateCarree(), cmap='jet',shading='auto')
plt.xticks(np.arange(-60,0,20))
plt.yticks(np.arange(50,90,10))
plt.title('sea ice sic_thickness_obs '+repr(last_year_thickness));
plt.colorbar(c, shrink=0.7, pad=0.02)
plt.pause(2)
