#!/usr/bin/env python

# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE) 
# ------------------------------------------------------------
# 
# PLOTTER
#  
# Plot NAME data on geographical map. Reads configuration file
# to set input data path, plot extent, normalisation, colormap
# and caption. Save output to PNG file.
# 
# Requires supporting libraries in namereader/.
# 
# EXAMPLES:
# 
# plotter.py --help
# plotter.py -c [config file]
# 

import argparse
import os
import calendar
import textwrap

from configobj import ConfigObj

# local NAME libraries
from pynameplot.namereader import *

"""
- plotter.py -

Read named configuration file
Load input NAME file, or subset of NAME files in directory
Set plot extent, normalisatiom, colormap, caption
Plot data mesh on Basemap
Save output to disk
"""

def drawMap(n, column):
    # Create Map object from NAME data
    m = namemap.Map(n, column=column)
    
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

    # Check for solid colouring flag
    if solid:
        m.solid = True
        if color1:
            m.drawSolid(column, color=color1)
        else:
            m.drawSolid(column)
    # Plot using colormap
    elif colormap:
        m.setColormap(colormap)
        m.drawMesh(column)
    else:
        m.setColormap()
        m.drawMesh(column)

    # Add station markers 1-6 if defined
    station_list = ['station1', 'station2', 'station3', 'station4', 'station5', 'station6']
    for station_name in station_list:
        station = config.get(station_name)
        if station:
            (station_lon, station_lat) = station
            m.addMarker(station_lon, station_lat)

    # Add shapefile overlays if selected
    if shapelist:
        files = []
        colors = []
        with open(shapelist, 'r') as f:
            for line in f:
                if "," in line:
                    (filename, colorname) = line.split(",", 1)
                    filename = filename.strip()
                    colorname = colorname.strip()
                    
                    files.append(filename)
                    colors.append(colorname)

        # Load zones into map object
        m.zoneLoad(files)

#        print m.patches # DEBUG

        # Draw lines at zone boundaries
        if shapelines:
            print 'Plotting zone lines...'
            m.zoneLines()
        
        # Draw solid colours for zones
        if shapecolors:
            print 'Plotting zone colours...'
            m.zoneColour(colors)

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
# Set helpfile text for configuration file options

epilog = textwrap.dedent("""
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
""")

parser = argparse.ArgumentParser(prog='plotter', formatter_class=argparse.RawDescriptionHelpFormatter, description='Plot NAME concentration files on world map', epilog=epilog)
parser.add_argument("-c", "--config", help="Configuration file", required=True)

args = parser.parse_args()

# ------------------------------------
# Configuration options

if not os.path.isfile(args.config):
    exit('*** ERROR: Configuration file {} not found!'.format(args.config))

config = ConfigObj(args.config, raise_errors=True, list_values=True)

# Reading configuration values

# input path
shapelist = config.get('shapelist') # Text file containing list of shapefiles
infile = config.get('infile') # Single input NAME file
indir = config.get('indir')  # Directory containing input NAME files

# time select
timestamp = config.get('timestamp')  # Plot data for given timestamp
day = config.get('day')   # Plot data summed for given day
week = config.get('week')   # Plot data summed for given week
month = config.get('month')   # Plot data summed for given month
year = config.get('year')    # Plot data summed for given year
sumall = config.get('sumall') # Set flag to sum all data in directory

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
runname = config.get('runname')  # Replace runname part of caption only #Marios added 24/10/2017

# shape overlays
shapelist = config.get('shapelist') # List of shapefiles and colours to plot
shapelines = config.get('shapelines') # Plot boundary lines for shapefiles
shapecolors = config.get('shapecolors') # Plot block colours for shapefiles

# output directory
outdir = config.get('outdir')  # Output directory for plot files, create if does not exist

# output file
outfile = config.get('outfile')  # Output plot file name root

# ------------------------------------


# read NAME data into object

if infile:
    n = name.Name(infile)
    if timestamp:
        # draw map for single timestamp
        column = timestamp
        n.column = column
        drawMap(n, column)
    else:
        # draw maps for all timestamps in file
        for column in n.timestamps:
            n.column = column
            drawMap(n, column)

elif indir:
    s = namesum.Sum(indir)
    column = 'total'

    if day:
        # draw summed map for day
        s.sumDay(day)
        if not caption:
            caption = "{} {} {} {}: {}{}{} day sum".format(s.runname, s.averaging, s.altitude, s.direction, s.year, s.month, s.day)
        if not outfile:
            outfile = "{}_{}{}{}_daily.png".format(s.runname, s.year, s.month, s.day)
        drawMap(s, column)

        
    elif week:
        # draw summed map for week
        s.sumWeek(week)
        if not caption:
            caption = "{} {} {} {}: {} week {} sum". format(s.runname, s.averaging, s.altitude, s.direction, s.year, week)
        if not outfile:
            outfile = "{}_{}{}_weekly.png".format(s.runnname, s.year, week.zfill(2))
        drawMap(s, column)

    elif month:
        # draw summed map for month
        s.sumMonth(month)
        if not caption:
            caption = "{} {} {} {}: {} {} sum". format(s.runname, s.averaging, s.altitude, s.direction, s.year, calendar.month_name[int(month)])
        if not outfile:
            outfile = "{}_{}{}_monthly.png".format(s.runname, s.year, month.zfill(2))
        drawMap(s, column)

    elif year:
        # draw summed map for year
        s.sumYear(year)
        if not caption:
            caption = "{} {} {} {}: {} year sum". format(s.runname, s.averaging, s.altitude, s.direction, year)
        if not outfile:
            outfile = "{}_{}_yearly.png".format(s.runname, year)
        drawMap(s, column)

    elif sumall:
        # draw summed map for entire directory
        s.sumAll()
        if not caption:
            caption = "{} {} {} {}: Summed".format(s.runname, s.averaging, s.altitude, s.direction)
        if not outfile:
            outfile = "{}_summed_all.png".format(s.runname)
        drawMap(s, column)

    else:
        # draw maps for all timestamps and files in directory
        allfiles = sorted(s.fs.getAll())

        for f in allfiles:
            n = name.Name(f)
            for column in n.timestamps:
                n.column = column
                drawMap(n, column)


else:
    raise ValueError('No input file or directory defined')

print '*** Done!'
