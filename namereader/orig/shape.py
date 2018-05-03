# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import geopandas as gpd
import os

from shapely.ops import cascaded_union

from .geom import reproj
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

        # reprojected geometry
        self.proj_geo = [reproj(g, self.lat_min, self.lat_max) for g in self.geo]
        self.proj_cu = reproj(self.cu, self.lat_min, self.lat_max)
