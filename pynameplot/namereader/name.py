# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# ------------------------------------------------------------
# 
# NAME
#
# Pandas/Geopandas data frame handling libraries for NAME
# geochemical datasets
# 

import numpy as np
import pandas as pd
import geopandas as gpd
import arrow

from shapely import speedups
from shapely.geometry import Point, Polygon

import os
import re

# local NAME libraries
from .header import loadheader
from .geom import coverfactor, gridsquare
from .shape import Shape
from util import shortname


class Name:
    """
    Define and create NAME data storage object
    """

    filename = ""
    timestamps = []  
    header = {}  

    def __init__(self, filename, crs = None):
        """
        Initialise NAME object

        filename -- path to NAME file
        crs -- coordinate reference system (defaults to EPSG:4326)
        """

        self.filename = filename
        if crs is None:
            crs = {'init': 'EPSG:4326'}
        self.crs = crs

        if not os.path.isfile(self.filename):
            raise Exception("Cannot find name file: {}".format(self.filename))

        # Enable Shapely native C++ acceleration
        if speedups.available:
            speedups.enable()

        # read and parse NAME file header
        self.header = loadheader(self.filename)

        # get grid size from header
        delta_lon = float(self.header['X grid resolution'])
        delta_lat = float(self.header['Y grid resolution'])
        
        lon_0 = float(self.header['X grid origin'])
        lat_0 = float(self.header['Y grid origin'])

        lon_size = int(self.header['X grid size'])
        lat_size = int(self.header['Y grid size'])

        mlon = (delta_lon*lon_size)
        mlat = (delta_lat*lat_size)

        lon_1 = lon_0+mlon
        lat_1 = lat_0+mlat

        self.lon_bounds=(lon_0, lon_1)
        self.lat_bounds=(lat_0, lat_1)

        self.grid_size = (delta_lon, delta_lat)

        # Set lat/lon gridline spacing according to grid size
        if mlon>60.0:
            steplon=20
        elif mlon>30.0:
            steplon=10
        else:
            steplon=5

        if mlat>60.0:
            steplat=20
        elif mlat>30.0:
            steplat=10
        else:
            steplat=5

        # Set lat/lon gridline minima to rounded values depending on scale
        lon_grid_min = int(lon_0) - int(lon_0) % steplon
        lat_grid_min = int(lat_0) - int(lat_0) % steplat

        # Store arrays for lat/lon gridline positions
        self.lon_grid=np.arange(lon_grid_min, lon_1, steplon).tolist()
        self.lat_grid=np.arange(lat_grid_min, lat_1, steplat).tolist()

        # LONGFIX: Normalise lon gridlines in range (-180, 180)
        # self.lon_grid = [np.mod((lg+180.0), 360.0) - 180.0 for lg in self.lon_grid]

        # Store header parameters as member variables
        self.runname = self.header['Run name']
        self.release = self.header['Start of release']
        self.endrelease = self.header['End of release']

        # Get field header values
        fields = pd.read_csv(self.filename, header=19, nrows=14)
        fields.drop(fields.columns[[0,1,2,3]], axis=1, inplace=True)

        # Store averaging time 
        field1 = fields[fields.columns[[0]]]
        self.ave = field1[6::1].values[0][0].strip()
        self.averaging = self.ave.replace(' integral','').replace('day ','days ').replace(' 0hr','').replace(' 0min','')
        self.timerun = self.averaging.split(" ")[0]
        self.releasetime = self.averaging.split(" ")[1]

        # Store run duration time
        dur = self.header['Run duration']
        self.duration = dur.replace('day ','days ').replace(' 0hr','').replace(' 0min','')

        # Store date information from input filename
        a = arrow.get(shortname(self.filename), 'YYYYMMDD')
        self.year = a.format('YYYY')
        self.month = a.format('MM').zfill(2)
        self.day = a.format('DD').zfill(2)

        # Get altitude range information from column header            
        self.alt = field1[13::1].values[0][0].strip()
        if 'Z = 50.0' in self.alt:
            self.altitude = '(0-100m)'
        elif 'Z = 500.0' in self.alt:
            self.altitude = '(0-1000m)'
        elif 'Z = 550.0' in self.alt:
            self.altitude = '(100-1000m)'
        elif 'Z = 2500.0' in self.alt:
            self.altitude = '(0-5000m)'
        elif 'Z = 5500.0' in self.alt:
            self.altitude = '(1-10km)'
        elif 'Z = 7000.0' in self.alt:
            self.altitude = '(4-10km)'
        else:
            self.altitude = ''

        # read CSV portion of NAME file into pandas DataFrame
        df = pd.read_csv(self.filename, header=31)

        # Clear bad (empty) data columns from DataFrame
        df = df.dropna(axis=1, how='all')
    
        # Get column header timestamp names from first row
        c = map(list, df[0:1].values)
        collist = c[0]
    
        # Set leader column names
        coordcols = ['X-Index', 'Y-Index', 'Longitude', 'Latitude']
        collist[1:4] = coordcols
        collist = [x.strip() for x in collist]
    
        # Get observation timestamp strings
        self.timestamps = collist[5::]

        # Determine whether simulation run is forwards or backwards in time
        if arrow.get(self.endrelease, 'DD/MM/YYYY HH:mm') > arrow.get(self.release, 'DD/MM/YYYY HH:mm'):
            self.direction = 'Forwards'
        else:
            self.direction = 'Backwards'

        # If run is backwards, modify timestamps to match self.ENDrelease header (per MP request)
        if self.direction == 'Backwards':
            col0_time = arrow.get(self.timestamps[0], 'DD/MM/YYYY HH:mm')
            start_time = arrow.get(self.endrelease, 'DD/MM/YYYY HH:mm')
            delta_time = start_time - col0_time
            
            newstamps = map(lambda t: (arrow.get(t, 'DD/MM/YYYY HH:mm')+delta_time).format('DD/MM/YYYY HH:mm UTC'), self.timestamps)
            self.timestamps = newstamps
            collist = [''] + coordcols + newstamps

        # Apply labels to DataFrame
        df.columns = collist[1::]
    
        # Drop leading rows
        df = df.drop([0, 1, 2, 3])
    
        # Convert strings to floats where possible
        df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    
        # Set mapping coordinate for GeoDataFrame
        # crs = {'init': 'epsg:4326'}

        # LONGFIX: Normalise longitude in range (-180, +180). 
        # df['Longitude'] = np.mod((df['Longitude']+180.0), 360) - 180.0
    
        # Generate Shapely Polygons for grid squares
        df['grid'] = [Polygon(gridsquare(xy + self.grid_size)) for xy in zip(df.Longitude, df.Latitude)]
    
        # Create GeoDataFrame with point and grid geometry columns
        self.data = gpd.GeoDataFrame(df, crs=self.crs, geometry=df['grid'])

        # Set lat/lon indices on data
        self.data.set_index(["Longitude", "Latitude"], inplace=True)

    def add_range(self, ts):
        """
        Sum given range of timestamp columns

        ts -- list of timestamp labels
        """

        self.data['subtotal'] = self.data[ts].sum(axis=1)

    def add_all(self):
        """
        Sum all timestamp columns found in file
        """

        self.data['subtotal'] = self.data[self.timestamps].sum(axis=1)

    def get_minmax(self):
        """
        Get minimum and maximum non-zero concentration data values for entire dataset
        """

        # Flatten list of concentration values
        cl = self.data[self.timestamps].values.tolist()
        flat = [item for sublist in cl for item in sublist]

        # Get minimum concentration value
        self.min_conc = min([x for x in flat if x > 0.0])

        # Get maximum concentration value
        self.max_conc = self.data[self.timestamps].values.max()
        
        return (self.min_conc, self.max_conc)

    def get_minmax(self, column):
        """
        Get minimum and maximum non-zero concentration values for given column
        """
        
        print 'Checking column:', column
        
        # Flatten list of concentration values
        cl = self.data[column].values.tolist()

        # Get minimum (non-zero) concentration value in column
        self.min_conc = min([x for x in cl if x > 0.0])

        # Get maximum concentration value in column
        self.max_conc = self.data[column].values.max()
        
        return (self.min_conc, self.max_conc)


    def trimmed(self):
        """
        Return only coordinate, subtotal columns
        """

        cols = ['grid', 'subtotal']
        return self.data[cols]

    def get_cover(self, shapefile):
        """
        Get covering factor value for input ESRI shapefile

        shapefile -- Path to ESRI shape file
        """
        # create shape object
        shape = Shape(shapefile)

        # calculate covering factors of shape cascaded union over grid squares
        self.data[shape.shortname] = [coverfactor(shape.cu, s) for s in self.data['grid']]
