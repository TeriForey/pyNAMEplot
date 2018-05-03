#!/usr/bin/env python  

import argparse
from shapely import speedups
from shapely.geometry import Polygon

from namereader import *

if speedups.available:
    speedups.enable()

parser = argparse.ArgumentParser(prog='check_valid', description='Check input shapefiles for Shapely validity')
parser.add_argument("-s", "--shapelist", help='File containing list of input shapefiles', required=True)
args = parser.parse_args()

print '+++ Starting check_valid... +++'

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

for f in files:

    shp = shape.Shape(f)
    print "Checking zone %s..." % shp.shortname
    poly = shp.cu
    print "Polygon type: %s Valid: %s" % (poly.exterior.type, poly.exterior.is_valid)
    # print poly
    poly2 = poly.buffer(0)
    print "Polygon type: %s Valid: %s" % (poly2.type, poly2.is_valid)

    print 

