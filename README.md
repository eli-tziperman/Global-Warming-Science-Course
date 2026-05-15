# Global-Warming-Science-Course

Resources for instructors using "Global Warming Science: A Quantitative Introduction to Climate Change and Its Consequences." Princeton University Press, 2022. More [here](https://courses.seas.harvard.edu/climate/eli/Courses/EPS101/textbook.html).

Included are Python scripts that prepare and can be used to update the data and code for students. The scripts retrieve either observations or CMIP climate output, mostly from the cloud, e.g., using Pangeo, minimizing manual data downloads when possible.

## Course website

https://courses.seas.harvard.edu/climate/eli/Courses/EPS101/index.html

Contains resources for students, including slides, lecture videos, data (pickle files), and Python Jupyter notebooks for in-class and homework use.


## Repository structure

Scripts for instructors and students are organized under Sources/ by textbook chapter. Each chapter folder contains the teaching staff scripts for that chapter and the resulting student resources. Slides are provided too, as Keynote and PDF files.

### Sources/

* Sources/Acidification/
* Sources/Boxes/
* Sources/Clouds/
* Sources/Critical-reading/
* Sources/Droughts/
* Sources/Floods/
* Sources/Forest-fires/
* Sources/Greenhouse/
* Sources/Heat-waves/
* Sources/Hurricanes/
* Sources/Ice-sheets/
* Sources/Introduction/
* Sources/Last-class/
* Sources/Mountain-glaciers/
* Sources/Ocean-circulation/
* Sources/Sea-ice/
* Sources/Sea-level/
* Sources/Temperature/

### Data-for-teaching-stuff/

The scripts for teaching staff mostly stream data from the original sites/cloud sources. Yet this directory contains smaller data sets that are easier to download and work on locally rather than stream directly from online sources. Same division into chapters as in Sources/

## License

MIT License — see LICENSE file. You are free to use, adapt, and redistribute
these scripts with attribution.

## Contact:

Eli Tziperman, eli@eps.harvard.edu,
Department of Earth and Planetary Sciences, Harvard University.

## Thanks to:
Joost van Asperen, for helping with the conversion of many scripts from reading local data to using the cloud, and with setting up the github site.
