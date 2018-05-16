NAME file analysis and plotting software
----------------------------------------
(c)2017 J. Duncan Law-Green, Kyubi Systems

pyNAMEplot provides a series of tools and functions to plot results of the Met Office dispersion model NAME. The package was designed for the data extraction and analysis work of Zoe Fleming, National Centre for Atmospheric Science (NCAS). Code was originally written by J. Duncan Law-Green (available [here](https://github.com/KyubiSystems/pynameplot)) and edited by Teri Forey at the University of Leicester.

### INSTALL

To install pre-built packages from Anaconda.org

```angular2html
conda install -c teriforey pynameplot
```

Note: pre-built binaries are not available for all operating systems.


### DOWNLOAD AND SET  ENVIRONMENT

Dependencies are available on Anaconda. To download and create the virtual environment required to run pyNAMEplot:

```angular2html
git clone https://github.com/TeriForey/pyNAMEplot
cd pyNAMEplot/
conda env create -f environment.yaml
source activate pynameplot
```

### SOFTWARE

There are three main pieces of software available for NAME processing and analysis:

* makemastergrid.py - given a list of ESRI shapefiles and an example NAME file, will 
  computer a 'master grid file' listing covering factors for each square in the input NAME grid.

* zonecsv.py - given a master grid file and a NAME file, or a directory containing NAME files, will 
  calculate summed particle concentrations by zone, outputting a CSV file, one row per timestamp in 
  the input name file(s).

* plotter.py - given a configuration file, will plot an input NAME file (or a sum of multiple NAME
  files) on a map.

### COMMAND-LINE HELP

Each software script has a simple help function which displays the options available on the command
line, accessible by appending '-h' or '--help' to the script name, e.g.

`./makemastergrid.py --help`

#### SHAPEFILE LIST

In order to build a master grid file, the first step is to compile an input list of the input ESRI
shapefiles used to denote the zones required. The shapefile list is a simple ASCII CSV file, with 
one row per ESRI zone, in the following format

`/path/to/shapefiles/filename.shp, Tomato`

The first element is the full path to the ESRI '.shp' shapefile, the second is the HTML colour 
desired for that zone on map plots.

#### MAKEMASTERGRID
```
usage: makemastergrid [-h] -n NAMEFILE -s SHAPELIST -o OUTFILE

Generate master grid file from ESRI zones.

optional arguments:
  -h, --help				show this help message and exit
  -n NAMEFILE, --namefile NAMEFILE  	Input NAME file to define grid shape
  -s SHAPELIST, --shapelist SHAPELIST   File containing list of input shapefiles
  -o OUTFILE, --outfile OUTFILE         Output master grid file name
										
```
#### ZONECSV
```
usage: zonecsv [-h] (-d INDIR | -n NAMEFILE) -g GRID -o OUTFILE
               [-w WEEK | -m MONTH | -y YEAR]

Sum NAME concentration files over ESRI zones.

optional arguments:
-h, --help				show this help message and exit
-d INDIR, --indir INDIR        		Input NAME file directory
-n NAMEFILE, --namefile NAMEFILE        Input NAME file to sum over
-g GRID, --grid GRID  			Input master grid file
-o OUTFILE, --outfile OUTFILE           Output CSV results file
-w WEEK, --week WEEK  			Select NAME files from ISO week number
-m MONTH, --month MONTH                 Select NAME files from Month number
-y YEAR, --year YEAR  			Select NAME files from Year

```
#### PLOTTER
```
usage: plotter [-h] -c CONFIG

Plot NAME concentration files on world map

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file

Configuration options:
----------------------

Configuration file is a plaintext file containing the plotting options to generate
the required output map plot.

infile:      Input NAME file -OR-
indir:       Directory containing input NAME files

timestamp:   Plot data for this specific timestamp
day:         Plot summed data for this day
week:        Plot summed data for this week (ISO-8601 week number)
month:       Plot summed data for this month
year:        Plot summed data for this year
sumall:      Set flag=True to sum all files in input directory

projection:  Map projection, default is 'cyl' (Cylindrical)
lon_bounds:  (Long_min, Long_max) tuple: Longitude bounds of plot
lat_bounds:  (Lat_min, Lat_max) tuple: Latitude bounds of plot
lon_axis:    (Lon1, Lon2, Lon3...) tuple: Lon scale tickmarks
lat_axis:    (Lat1, Lat2, Lat3...) tuple: Lat scale tickmarks

scale:       (Min, Max) scale tuple for plotting values, default is (5e-9, 1e-4) 
autoscale:   Set flag=True for scaling colormap by min/max data values

colormap:    Matplotlib colormap name to be used for data, default is 'rainbow'

solid:       Set flag=True for solid region plotting
color1:      Name of solid colour for dataset 1 if solid flag set

caption:     Override default plot caption and use this text string

shapelist:   Text file containing list of ESRI shapefiles
shapelines:  Set flag=True to plot boundary lines for shapefiles
shapecolors: Set flag=True to plot solid colours for shapefiles

outdir:      Output directory for plot files, create if does not exist
```
