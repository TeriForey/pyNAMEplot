# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, version 2.0 (see LICENSE)
# ------------------------------------------------------------
#
# GEOM
# 
# Support libraries. Perform geometrical calculations on NAME data
# grid cells.
#

import os

from shapely.ops import transform, cascaded_union
from shapely.geometry import Point, Polygon

# --------------------------------------
def coverfactor(geom, square):
    """
    Calculate covering factor of ESRI shape over grid square.
    Value is float in range 0.0 -- 1.0

    geom -- Shapely geometry
    square -- Shapely geometry of grid square
    lat_min -- reference latitude 1
    lat_max -- reference latitude 2
    """

    cf = 0.0

    # geometry of intersection between input shape and grid square
    inters = geom.intersection(square)
        
    # ratio of areas is covering factor
    cf += (inters.area/square.area)
    
    return cf


# --------------------------------------
def gridsquare(coords):
    """
    Generate list of coordinates for gridsquare
    coords -- 4-tuple of grid centre coords, dlongitude, dlatitude
    
    returns list of 4 (lon, lat) coords for grid corners
    """

    (lon, lat, dlon, dlat) = coords
    gs = [(lon - dlon/2., lat - dlat/2.), (lon - dlon/2., lat + dlat/2.), (lon + dlon/2., lat + dlat/2.), (lon + dlon/2., lat - dlat/2.)]
    return gs
