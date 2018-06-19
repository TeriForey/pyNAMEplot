#!/usr/bin/env python

# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# -------------------------------------------------------------
#
# MULTIPLOTTER_FILLCONTOUR
#
# Plot multiple NAME datasets on geographical map, with concentrations
# shown as filled contours. Reads configuration file to set input data
# paths, plot extent, normalisation, colormap and caption. Save output
# to PNG file.
#
# Requires supporting libraries in namereader/.
#
# EXAMPLES:
#
# multiplotter_fillcontour.py --help
# multiplotter_fillcontour -c [config file]
#

import argparse
import matplotlib
import os
import re
import gc
import calendar
import numpy as np

from configobj import ConfigObj

# local NAME libraries
from pynameplot.namereader import *

"""
- multiplotter_fillcontour -

Read named configuration file
Load input NAME file, or subset of NAME files in directory
Set plot extent, normalisatiom, colormap, caption
Plot data mesh on Basemap
Repeat for subsequent files or directories
Save output to disk
"""

def drawMap(n, column, runname=''):
    # Create Map object from NAME data
    m = namemap.Map(n, column=column, runname=runname)
    m.runnames = []
    
    # Set projection if defined, otherwise cylindrical
    if projection:
        m.setProjection(projection)
        
    # Set map bounds from config file, otherwise scale by grid file
    if lon_bounds and lat_bounds:
        m.setBounds(lon_bounds, lat_bounds)
    else:
        m.setBounds(n.lon_bounds, n.lat_bounds)
            
    # Set map axes from config file, else scale by grid file
    if lon_axis and lat_axis:
        lon = [float(i) for i in lon_axis]
        lat = [float(i) for i in lat_axis]
        m.setAxes(lon, lat)
    else:
        m.setAxes(n.lon_grid, n.lat_grid)
        
    # Set scale if defined, otherwise standard scale
    # set other option for autoscale?
    if scale:
        (scale_min, scale_max) = scale
        m.setFixedScale(scale_min, scale_max)
    elif autoscale:
        m.setAutoScale(column)

    # Set up data grid
    if caption:
        m.drawBase(caption, fontsize=8)
    else:
        m.drawBase(m.caption, fontsize=8)

    # Add station markers 1-6 if defined
    for i in xrange(1,7):
        station = config.get('station' + str(i))
        if station:
            (station_lon, station_lat) = station
            x,y = m.m(float(station_lon), float(station_lat))
            m.m.plot(x,y,'kx', markersize=4, color='black', zorder=25)

    return m


def addSettoMap(m, n, i, column):

    """
    Add additional NAME file to output plot
    Assumes solid colour for footprint plotting

    m: existing Map object
    n: new Name object to add to plot
    i: index number of new dataset in config file
    column: name of data column to plot
    """

    m.runnames.append(n.runname)
    
    color = add_color[i]
    zorder = i+20

    mesh = n.data[column]
    mesh1 = mesh.loc[mesh > 0.0]
    
    mesh2 = mesh1.unstack(level=1)
    mesh2 = mesh2.fillna(0)
    
    lons = mesh2.index.get_level_values('Longitude')
    lats = mesh2.columns
    
    mesh2 = mesh2.transpose()
    
    x,y = m.m(lons, lats)
    
    rgba = matplotlib.colors.to_rgba(color, alpha=0.3)
    cmap = matplotlib.colors.ListedColormap([rgba])

    xp = np.tile(x, (y.shape[0], 1))
    yp = np.tile(y, (x.shape[0], 1)).transpose()

    cont = m.m.contour(xp, yp, mesh2, (1.e-9,1000.0), colors=(color, 'white'), linewidths=(0.6, 0.6), zorder=zorder)
    cont = m.m.contourf(xp, yp, mesh2, (1.e-9,1000.0), colors=(color, 'white'), alpha=0.3, linewidths=(0.6, 0.6), zorder=zorder)
    
    return m
	

def saveMap(m):

    # Add legend
    proxy = [matplotlib.pyplot.Rectangle((0,0),1,1,fc=color) for color in add_color.values()]
    matplotlib.pyplot.legend(proxy, m.runnames, loc='upper right', fontsize='small').set_zorder(102)
    
    matplotlib.pyplot.show()

    # Save output map plot to disk
    
    # If output directory does not exist, create it
    if outdir:
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        m.outdir = outdir

    # Save output to disk
    if outfile:
        m.saveFile(filename=outfile)
    else:
        m.saveFile()


# ------------------------------------
parser = argparse.ArgumentParser(prog='plotter', description='Plot NAME concentration files on world map')
parser.add_argument("-c", "--config", help="Configuration file", required=True)

args = parser.parse_args()

# ------------------------------------
# Configuration options

if not os.path.isfile(args.config):
    exit('*** ERROR: Configuration file {} not found!'.format(args.config))

config = ConfigObj(args.config, raise_errors=True, list_values=True)

# Reading configuration values

# input ESRI shapefile list
shapelist = config.get('shapelist') # Text file containing list of shapefiles

# input path 1 
infile = config.get('infile') # Single input NAME file
indir = config.get('indir')  # Directory containing input NAME files

# time select
timestamp = config.get('timestamp')  # Plot data for given timestamp
day = config.get('day')   # Plot data summed for given day
week = config.get('week')   # Plot data summed for given week
month = config.get('month')   # Plot data summed for given month
year = config.get('year')    # Plot data summed for given year

# map geometry
projection = config.get('projection')  # Map projection, default is 'cyl' (Cylindrical)
lon_bounds = config.get('lon_bounds')  # (Long_min, Long_max) tuple: Longitude bounds of plot
lat_bounds = config.get('lat_bounds')  # (Lat_min, Lat_max) tuple: Latitude bounds of plot
lon_axis = config.get('lon_axis')  # (Lon1, Lon2, Lon3...) tuple: Lon scale tickmarks
lat_axis = config.get('lat_axis')  # (Lat1, Lat2, Lat3...) tuple: Lat scale tickmarks

# map colour
scale = config.get('scale') # (Min, Max) scale tuple for plotting values, default is (5e-9, 1e-4)
autoscale = config.get('autoscale') # Set flag for scaling colormap by min/max data values

colormap = config.get('colormap')  # Matplotlib colormap name to be used for data, default is 'rainbow'

solid = config.get('solid')  # Set flag for solid region plotting
color1 = config.get('color1')   # Solid colour for dataset 1

# map labelling
caption = config.get('caption')  # Primary caption for output plot
runname = config.get('runname')  # Replace runname part of caption only

# output directory
outdir = config.get('outdir')  # Output directory for plot files, create if does not exist

# output file
outfile = config.get('outfile')  # Output plot file name root

# ------------------------------------

# read supplemental NAME parameters, if set
add_file = {}
add_dir = {}
add_color = {1: color1}

for i in xrange(2,7):
    if config.get('infile' + str(i)):
        add_file[i] = config.get('infile' + str(i))
    if config.get('indir' + str(i)):
        add_dir[i] = config.get('indir' + str(i))
    if config.get('color' + str(i)):
        add_color[i] = config.get('color' + str(i))

# read NAME data into object

print add_dir

if infile:
    n = name.Name(infile)
    if timestamp:
        # draw map for single timestamp
        column = timestamp
        n.column = column
        map_obj = drawMap(n, column)
        map_obj = addSettoMap(map_obj, n, 1, column)

        for i in xrange(2,7):
            if i in add_file:
                n_i = name.Name(add_file[i])
                map_obj = addSettoMap(map_obj, n_i, i, column)
        saveMap(map_obj)
            

    else:
        # draw maps for all timestamps in file
        for column in n.timestamps:
            n.column = column
            map_obj = drawMap(n, column, runname)
            map_obj = addSettoMap(map_obj, n, 1, column)

            for i in xrange(2,7):
                if add_file[i]:
                    n_i = name.Name(add_file[i])
                    map_obj = addSettoMap(map_obj, n_i, i, column)
            saveMap(map_obj)

elif indir:
    s = namesum.Sum(indir)

    if day:
        # draw summed map for day
        s.sumDay(day)
        if not caption:
            caption = "{} {} {} {}: {}{}{} day sum".format(runname or s.runname, s.averaging, s.altitude, s.direction, s.year, s.month, s.day)
        if not outfile:
            outfile = "{}_{}{}{}_daily.png".format(runname or s.runname, s.year, s.month, s.day)
        map_obj = drawMap(s, 'total')
        map_obj = addSettoMap(map_obj, s, 1, 'total')

        for i in add_dir:
            s_i = namesum.Sum(add_dir[i])
            s_i.sumDay(day)
            map_obj = addSettoMap(map_obj, s_i, i, 'total')
        saveMap(map_obj)

        
    elif week:
        # draw summed map for week
        s.sumWeek(week)
        if not caption:
            caption = "{} {} {} {}: {} week {} sum". format(runname or s.runname, s.averaging, s.altitude, s.direction, s.year, week)
        if not outfile:
            outfile = "{}_{}{}_weekly.png".format(runname or s.runnname, s.year, week.zfill(2))
        map_obj = drawMap(s, 'total')
        map_obj = addSettoMap(map_obj, s, 1, 'total')

        for i in add_dir:
            s_i = namesum.Sum(add_dir[i])
            s_i.sumWeek(week)
            map_obj = addSettoMap(map_obj, s_i, i, 'total')
        saveMap(map_obj)

        
    elif month:
        # draw summed map for month
        s.sumMonth(month)
        if not caption:
            caption = "{} {} {} {}: {} {} sum". format(runname or s.runname, s.averaging, s.altitude, s.direction, s.year, calendar.month_name[int(month)])
        if not outfile:
            outfile = "{}_{}{}_monthly.png".format(runname or s.runname, s.year, month.zfill(2))
        map_obj = drawMap(s, 'total')
        map_obj = addSettoMap(map_obj, s, 1, 'total')

        for i in add_dir:
            s_i = namesum.Sum(add_dir[i])
            s_i.sumMonth(month)
            map_obj = addSettoMap(map_obj, s_i, i, 'total')
        saveMap(map_obj)

        
    elif year:
        # draw summed map for year
        s.sumYear(year)
        if not caption:
            caption = "{} {} {} {}: {} year sum". format(runname or s.runname, s.averaging, s.altitude, s.direction, year)
        if not outfile:
            outfile = "{}_{}_yearly.png".format(runname or s.runname, year)
        map_obj = drawMap(s, 'total')
        map_obj = addSettoMap(map_obj, s, 1, 'total')

        for i in add_dir:
            s_i = namesum.Sum(add_dir[i])
            s_i.sumYear(year)
            map_obj = addSettoMap(map_obj, s_i, i, 'total')
        saveMap(map_obj)

        
    else:
        # draw maps for all timestamps and files in directory
        allfiles = {}

        # date-sorted list of files in initial directory
        allfiles[1] = sorted(s.fs.getAll())

        # date-sorted lists of files for input directories 2-6
        for i in xrange(2,7):
            indir_i = config.get('indir' + str(i))
            if indir_i:
                s_i = namesum.Sum(indir_i)
                allfiles[i] = sorted(s_i.fs.getAll())

        # iterate over all files in base directory
        for f in allfiles[1]:
            n = name.Name(f)

            # Extract date from base filename
            mapdate = re.findall('\d{8}', f)[0]

            # Iterate over timestamps in base file and draw base map
            for column in n.timestamps:
                n.column = column
                map_obj = drawMap(n, column, runname)
                map_obj = addSettoMap(map_obj, s, 1, column)

                # iterate over input directories 2-6
                for i in allfiles.keys()[1:]:
                    
                    # Check for date in list of files
                    match_date = [ m for m in allfiles[i] if mapdate in m ]

                    # If found, and timestamp exists in target file
                    if match_date:
                        n_i = name.Name(match_date[0])
                        if column in n_i.timestamps:
                            map_obj = addSettoMap(map_obj, n_i, i, column)

                # Save output map to disk
                saveMap(map_obj)

            # Force manual garbage collection
            gc.collect()
              

else:
    raise ValueError('No input file or directory defined')
    exit


print '*** Done!'
