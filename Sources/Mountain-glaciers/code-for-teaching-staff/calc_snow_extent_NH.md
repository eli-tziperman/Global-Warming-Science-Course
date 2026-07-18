# Northern Hemisphere Snow Cover Calculation

This note describes the calculation implemented in `calc_snow_extent_NH.py`.

## Input data

The script uses the consolidated AVHRR10C1.V4 climate data record:

Xiao, X., Naegeli, K., Premier, V., Li, S., Neuhaus, C., Wiesmann, A., and Wunderle, S. (2026). Introduction to a 45-year (1979-2023) global daily snow cover fraction product from multiple AVHRR satellites with accuracy assessment. *Remote Sensing of Environment*, 334, 115235. https://doi.org/10.1016/j.rse.2026.115235

Dataset:

Xiao, X., Naegeli, K., Premier, V., Li, S., Neuhaus, C., and Wunderle, S. (2025). *A 45-year (1979-2023) Global Daily Snow Cover Fraction Climate Data Record from multiple AVHRR satellites (AVHRR10C1.V4)*. Zenodo. https://doi.org/10.5281/zenodo.16746237

This product is preferable to manually stitching the CEDA `AVHRR_SINGLE/v4.0` files because it is already consolidated from multiple AVHRR sensors and includes the multi-sensor compositing and spatiotemporal gap-filling framework described by Xiao et al. (2026).

## Downloaded files

When raw data are needed, the script downloads these Zenodo archives:

- `1979-1989.7z`
- `1990-1999.7z`
- `2000-2009.7z`
- `2010-2023.7z`

Archives are saved under:

`~/Downloads/snow-cover-data/archives/`

Extracted daily GeoTIFFs are saved under:

`~/Downloads/snow-cover-data/AVHRR10C1_V4/`

The script uses `bsdtar` to extract the `.7z` archives. A complete monthly-area
cache bypasses all raw-data setup. If cached months are missing, the script uses
the cached GeoTIFF index when available; only when that index is absent does it
check the extraction markers and download any unextracted archive.

## Monthly snow-covered area

The AVHRR10C1.V4 GeoTIFF values are:

- `0-100`: snow cover fraction (%)
- `205`: cloud
- `206`: polar night
- `210`: water
- `215`: glacier, ice caps, ice sheets
- `254`: no satellite acquisition/error

The script uses the **SCFG** files, i.e., the snow cover fraction on the ground. For each month:

1. Each daily GeoTIFF is restricted to the rows needed for the Northern Hemisphere ERA5-Land grid, including the first row south of the equator for the target cell centered on 0 degrees.
2. Pixels with `0 <= SCFG <= 100` are treated as valid fractional snow-cover observations.
3. For each grid cell, the script averages all valid daily SCFG values within the month.
4. A grid cell is retained only if it has at least **five** valid daily observations in that month.
5. The 0.05-degree monthly field is aligned to the ERA5-Land grid and averaged into 0.1-degree cells. Interior target cells average as many as four valid constituent AVHRR cells.
6. Only target cells that are valid in the ERA5-Land land product are retained.
7. The retained 0.1-degree monthly mean SCFG field is converted to snow-covered area as `cell_area * monthly_mean_SCFG / 100`.
8. Flagged AVHRR pixels, including cloud, polar night, water, glacier/ice-sheet, and no-acquisition/error pixels, do not contribute to the monthly mean. Cells with fewer than five valid observations are excluded before aggregation.

This follows the Fig. 17 SCA anomaly method in Xiao et al. (2026): monthly SCF fields are computed first over the Northern Hemisphere, retaining grid cells with at least five clear-sky observations per month, and the 0.05-degree fields are aggregated to the 0.1-degree ERA5-Land grid before spatial aggregation to SCA. The script uses the ground-snow product (**SCFG**) rather than the viewable-snow product (**SCFV**) because the target quantity is snow cover on the ground.

The ERA5-Land validity mask is obtained from the finite grid cells in the March 1979 monthly snow-cover field downloaded from the Copernicus Climate Data Store. ERA5-Land uses a static land domain, so the field supplies the target grid and its land-validity mask without using ERA5 snow-cover values in the AVHRR calculation. The unused 90-degree row contains no valid ERA5-Land cells and is omitted, leaving the 89.9 degrees N to 0 degrees grid used in the area calculation.

Unlike the earlier CEDA single-sensor implementation, the script does not do its own same-day satellite candidate selection or temporal gap filling. Those steps are handled upstream in the consolidated AVHRR10C1.V4 product.

The monthly cache is saved to:

`~/Downloads/snow-cover-data/monthly_nh_scfg_area_xiao_fig17a_era5land_0p1_v1_mkm2.csv`

It contains:

- `time`: month
- `area`: Northern Hemisphere monthly SCFG snow-covered area in million km²
- `valid_area`: area of retained 0.1-degree ERA5-Land cells with at least one constituent 0.05-degree pixel having five valid observations, in million km²
- `daily_files`: number of daily GeoTIFFs used for that month

Each newly calculated month is written to this cache immediately, so an interrupted run resumes from the next missing month.

The GeoTIFF file index is saved as:

`~/Downloads/snow-cover-data/avhrr10c1_v4_scfg_tiff_index_1979_2023.csv`

## Grid-cell area

Area is calculated after aggregation on the 0.1-degree ERA5-Land latitude-longitude grid. For each latitude row, cell area is:

`area = R^2 * abs(sin(lat_north) - sin(lat_south)) * abs(lon_east - lon_west)`

where `R = 6371.0088 km` and `lon_east - lon_west = 0.1 degrees`. The result
is in square kilometers and is divided by `1e6` to report million square
kilometers.

## Reproducibility limits of Fig. 17

Xiao et al. (2026) specify the two central processing steps for Fig. 17: forming monthly 0.05-degree SCF averages from cells with at least five clear-sky observations and then averaging four constituent pixels onto the 0.1-degree ERA5-Land grid. They do not, however, provide enough implementation detail to reproduce the plotted SCFG curve exactly. The paper does not state the precise SCA integration formula, how a target cell is treated when only one to three of its four AVHRR constituents are valid, which land-water mask is used, whether changing monthly valid area is normalized or restricted to a fixed spatial domain, or the exact anomaly convention and treatment of months with missing daily files. Neither the paper nor its supplement provides the 45 plotted SCFG values or the analysis code. Here we use a spherical area-weighted sum of fractional SCFG, the ERA5-Land finite-cell mask, every target cell with at least one valid constituent, and anomalies relative to the complete 1979-2023 March mean. Tests using the native AVHRR land mask or requiring all four constituents did not improve agreement with the digitized Fig. 17a curve, while a simple valid-area normalization produced only a small improvement. The remaining mismatch therefore likely reflects one or more undocumented processing choices, or a difference between the public data and the version used to prepare the figure.

## Seasonal anomalies

The monthly Northern Hemisphere snow-covered area is resampled into seasonal means using quarters starting in December:

`QS-DEC`

This gives:

- DJF: December-February
- MAM: March-May
- JJA: June-August
- SON: September-November

Seasons are retained only when all three monthly values are present so partial seasons at the beginning or end of the record do not affect the regression.

For each season, the script subtracts that season's 1979-2023 mean snow-covered area from every seasonal value. The plotted series and fitted linear trend are therefore seasonal SCA anomalies in million km², analogous to the March Northern Hemisphere SCA anomalies shown in Fig. 17 of Xiao et al. (2026), but extended here to DJF, MAM, JJA, and SON.

The seasonal dictionary saved for students is:

`Output/to-pickle/snow_extent_north_hemisphere.npy`

Each season contains:

- `time`: season timestamp
- `area`: seasonal mean monthly SCFG snow-covered area in million km²
- `anomaly`: seasonal SCA anomaly in million km²

The seasonal figure is saved as:

`Output/snow-cover-seasonal-timeseries.pdf`

## Monthly and March anomalies

For each calendar month, the script subtracts that month's 1979-2023 mean from its 45 annual values and fits an ordinary least-squares linear trend. The 12-panel legend reports the trend in million km² per decade and its $R^2$. The monthly figure is saved as:

`Output/snow-cover-monthly-timeseries.pdf`

The March-only figure with a wide aspect ratio for visual comparison with Fig. 17a of Xiao et al. (2026) is saved as:

`Output/snow-cover-march-scfg-anomaly-xiao17a-aspect.pdf`

Its plotting box uses the measured Fig. 17a panel aspect ratio from Xiao et al. (2026), `1010/487 = 2.0739`, with y-limits of `-7` to `7` million km² and x-limits matching the padded 1979-2023 March record shown in the paper.

The monthly dictionary saved for students is:

`Output/to-pickle/snow_area_monthly_north_hemisphere.npy`

Each calendar month contains `time`, `area`, and `anomaly` series.

## Reproducing the calculation

Run:

```bash
python calc_snow_extent_NH.py
```

If the monthly cache is incomplete and the ERA5-Land mask source is absent, the run also requires `cdsapi` and configured Copernicus CDS credentials in `~/.cdsapirc`.

For a short test run after the archives have been downloaded and extracted:

```bash
SNOW_CCI_MAX_MONTHS=3 python calc_snow_extent_NH.py
```

The partial monthly results are cached, but figures are not written until all
540 study months have been processed.
