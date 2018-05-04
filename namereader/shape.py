# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# ------------------------------------------------------------
#
# SHAPE
#
# Support libraries. Generate Shapely shape data object from ESRI shapefile
# 

import geopandas as gpd
import os

from shapely.ops import cascaded_union

from .util import shortname


class Shape(object):
    """
    Class for Shapely geometry derived from ESRI shapefile
    """

    shapefile = ""
    shortname = ""

    def __init__(self, shapefile):
        """
        Initialise shape object from ESRI file
        filename -- path to ESRI shapefile
        """

        self.shapefile = shapefile
        
        if not os.path.isfile(self.shapefile):
            raise ValueError

        self.shortname = shortname(self.shapefile)

        self.data = gpd.GeoDataFrame.from_file(self.shapefile)

        # Get shape latitude extent
        self.geo = self.data.geometry
        self.cu = cascaded_union(self.geo)
        self.bounds = self.cu.bounds
        self.lat_min = self.geo.bounds['miny'].min()
        self.lat_max = self.geo.bounds['maxy'].max()

    def is_valid(self):
        poly = self.cu
        poly2 = poly.buffer(0)
        if poly.exterior.is_valid and poly2.is_valid:
            return True
        else:
            return False

