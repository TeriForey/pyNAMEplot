#!/usr/bin/env python

from pyproj import Proj, transform
import fiona
from fiona.crs import from_epsg
from os.path import basename, splitext
import argparse


def main():
    parser = argparse.ArgumentParser(description='Re-projects shapefile')
    parser.add_argument('shp', help='ShapeFile to re-project')
    parser.add_argument('-p', '--projection', type=int, default=4326, help="New EPSG projection (default: %(default)s)")

    args = parser.parse_args()

    shape_file = args.shp
    out_file = basename(splitext(shape_file)[0]) + '_EPSG{}'.format(args.projection)
    print 'Writing output {}...'.format(out_file)

    shape = fiona.open(shape_file)
    original = Proj(shape.crs) # Input CRS
    destination = Proj(init='EPSG:{}'.format(args.projection)) # Output CRS
    linearRing = []

    with fiona.open(out_file, 'w', 'ESRI Shapefile', shape.schema.copy(), crs=from_epsg(args.projection)) as output:
        for feat in shape:
            for point in feat['geometry']['coordinates'][0]:
                lon,lat,zcoord = point
                x,y = transform(original, destination,lon,lat)
                linearRing.append((x,y))
            # change only the coordinates of the feature
            feat['geometry']['coordinates'] = [linearRing]
            output.write(feat)


if __name__ == "__main__":
    main()
