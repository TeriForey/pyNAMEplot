#!/usr/bin/env python

# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# ------------------------------------------------------------
#
# MAKEMASTERGRID
#
# Take list of input ESRI shapefiles, and example input NAME file
# (for gridding information) and create master grid file, which
# gives filling factor (in range 0.0 -- 1.0) for each shapefile per
# grid cell. Output grid data saved in Python 'pickle' format.
#
# Requires supporting libraries in namereader/.
#
# EXAMPLES:
#
# makemastergrid.py --help
# makemastergrid.py -n [NAME file] -s [list of shape files] -o [output grid file]
#

import argparse
import numpy as np
import pandas as pd
import geopandas as gpd
import itertools

from shapely import speedups
from shapely.geometry import Polygon

from pynameplot.namereader import *

if speedups.available:
    speedups.enable()

# ------------------------------------

parser = argparse.ArgumentParser(prog='makemastergrid', description='Generate master grid file from ESRI zones.')
parser.add_argument("-n", "--namefile", help='Input NAME file to define grid shape', required=True)
parser.add_argument("-s", "--shapelist", help='File containing list of input shapefiles', required=True)
parser.add_argument("-o", "--outfile", help='Output master grid file name', required=True)
args = parser.parse_args()

# ------------------------------------

print '+++ Starting makemastergrid... +++'

# Read list of shapefiles, colours

print "Reading shape list %s..." % args.shapelist

files = []
colors = []

with open(args.shapelist, 'r') as shp:

    for line in shp:
        if "," in line:
            (shapename, colorname) = line.split(",", 1)
            shapename = shapename.strip()
            colorname = colorname.strip()

            files.append(shapename)
            colors.append(colorname)

shortnames = [ util.shortname(f) for f in files ]
pcnames = [ 'pc_' + s for s in shortnames ]

# Get CRS from first shapefile
s = gpd.read_file(files[0])

print 'CRS found: ', s.crs

# ------------------------------------
# Read NAME file header for grid parameters

print "Parsing header %s..." % args.namefile

head = header.loadheader(args.namefile)

x0 = float(head['X grid origin'])
y0 = float(head['Y grid origin'])
xsize = float(head['X grid size'])
ysize = float(head['Y grid size'])
xstep = float(head['X grid resolution'])
ystep = float(head['Y grid resolution'])

grid_size = (xstep, ystep)

x1 = x0 + ((xsize-1) * xstep)
y1 = y0 + ((ysize-1) * ystep)

xcol = np.linspace(x0, x1, xsize)  # Longitude axis
ycol = np.linspace(y0, y1, ysize)  # Latitude axis

longitude = []
latitude = []

for (colx, coly) in itertools.product(xcol, ycol):
    longitude.append(colx)
    latitude.append(coly)

# ------------------------------------

data = { 'Longitude': longitude, 'Latitude': latitude }
df = pd.DataFrame(data)
df = df[['Longitude', 'Latitude']]  # Set column order manually

# Generate polygon geometry column
df['grid'] = [ Polygon(geom.gridsquare(xy + grid_size)) for xy in zip(df.Longitude, df.Latitude) ]

# Create GeoDataFrame using CRS from provided shapefiles
gd = gpd.GeoDataFrame(df, crs=s.crs, geometry=df['grid'])

print "Starting covering factor calculations..."

# Loop over input shapefiles
for f in files:

    shp = shape.Shape(f)
    print "Processing zone %s..." % shp.shortname

    cover = gpd.sjoin(gd, shp.data, how='inner', op='intersects')

    cover[shp.shortname] = [geom.coverfactor(shp.cu, s) for s in cover['grid']]

    c2 = cover[shp.shortname]

    if not c2.index.is_unique:

        print "Removing duplicate index for %s" % shp.shortname
        c2 = c2[~c2.index.duplicated(keep='first')]


    gd = gd.join(c2)

# Replacing NaNs
gd = gd.fillna(0)

gd = gd.set_index(['Longitude', 'Latitude'])

# Set sparse to reduce on-disk filesize
gd = gd.to_sparse(fill_value=0)

# Write pickle file
print "Writing output file %s..." % args.outfile
gd.to_pickle(args.outfile)

print "=== Done! ==="
