#!/usr/bin/env python

from pyproj import Proj, transform
import fiona
import sys
from fiona.crs import from_epsg
from os.path import basename, splitext

shape_file = sys.argv[1]
out_file = basename(splitext(shape_file)[0]) + '_new'
print 'Writing output {}...'.format(out_file)

shape = fiona.open(shape_file)
original = Proj(shape.crs) # Input CRS
destination = Proj(init='EPSG:4326') # Output CRS
linearRing = []

with fiona.open(out_file, 'w', 'ESRI Shapefile', shape.schema.copy(), crs=from_epsg(4326)) as output:
    for feat in shape:
        for point in feat['geometry']['coordinates'][0]:
            lon,lat = point
            x,y = transform(original, destination,lon,lat)
            linearRing.append((x,y))
        # change only the coordinates of the feature
        feat['geometry']['coordinates'] = [linearRing]
        output.write(feat)
