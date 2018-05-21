# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# ------------------------------------------------------------
#
# NAMEMAP
#
# Support libraries. Generate Matplotlib Basemap map plots for NAME geochemical
# data sets.
#

import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.collections import PatchCollection
from PIL import Image
import arrow

from shapely.ops import transform
from shapely.geometry import Point, Polygon
from descartes import PolygonPatch
import geopandas as gpd

import os

# suppress matplotlib/basemap warnings
import warnings
warnings.filterwarnings("ignore")



class Map(object):

    """
    Define and create a visualisation plot
    from NAME concentration data
    """

    lon_range = []
    lat_range = []
    lon_axis = []
    lat_axis = []

    conc = []

    def __init__(self, name, column='total', runname=''):
        """
        Initialise Map object.

        name   -- a loaded Name object containing parsed data
        column -- column name to plot. Default is 'total' column from summed file.

        Default is to set auto-scale normalisation from
        extremal values of input data.
        """

        self.name = name
        self.column = column
        self.runname = runname
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect('equal')
        self.solid = False

        self.outdir = ''

        # Set default plot caption
        self.getCaption()

        # set default plot filename
        self.getFilename()

        # set default projection to cylindrical
        self.projection = 'cyl'

        # set default fixed scale normalisation for output plot
        self.setFixedScale()

    def getCaption(self):
        """
        Set default plot caption
        """

        if self.name.direction == 'Forwards':
            release_date = self.name.release[0:10]
        elif self.name.direction == 'Backwards':
            release_date = self.name.endrelease[0:10]

        if self.column == 'total':
            suffix = 'Sum'
        else:
            a = arrow.get(self.column, 'DD/MM/YYYY HH:mm')
            suffix = a.format('HHmm')
            if self.name.direction == 'Forwards':
                suffix = a.shift(hours=-3).format('HHmm')

        self.caption = '{} {} {} {} start of release: {} {}'.format(self.runname or self.name.runname, self.name.averaging, self.name.altitude, self.name.direction, release_date, suffix)

    def getFilename(self):
        """
        Set default plot filename
        """
        # get root of input NAME filename
        base = os.path.basename(self.name.filename)
        base = os.path.splitext(base)[0]

        if self.column == 'total':
            suffix = 'sum_day'
        else:
            a = arrow.get(self.column, 'DD/MM/YYYY HH:mm')
            suffix = a.format('HHmm')
            if self.name.direction == 'Forwards':
                suffix = a.shift(hours=-3).format('HHmm')

        self.filename = '{}_{}.png'.format(base, suffix)

    def setFixedScale(self, conc=(5.e-9, 1.e-5)):

        """
        Set fixed scale normalisation manually.

        conc -- 2-tuple containing (min, max) values of concentration scale
        """

        if not (len(conc) == 2):
            raise ValueError('Invalid concentration range array')

        self.norm = matplotlib.colors.LogNorm(vmin=conc[0], vmax=conc[1], clip=False)

    def setAutoScale(self, column=None):
        """
        Set autoscale normalisation.

        column -- Name of data column to extract (min, max) values for scale normalisagtion
        """

        if column is None:
            column = self.column

        self.name.get_minmax(column)

        # set default normalisation from name file extrema
        self.norm = matplotlib.colors.LogNorm(vmin=self.name.min_conc, vmax=self.name.max_conc, clip=False)

    def setBounds(self, lon_range, lat_range):
        """
        Set map latitude and longitude bounds.

        lon_range -- 2-tuple containing (lon_min, lon_max)
        lat_range -- 2-tuple containing (lat_min, lat_max)
        """

        if not (len(lon_range) == 2 and len(lat_range) == 2):
            raise ValueError('Invalid longitude/latitude range')

        #self.lon_range = lon_range
        self.lon_range = [float(b) for b in lon_range]
        self.lat_range = [float(b) for b in lat_range]

    def setAxes(self, lon_axis, lat_axis):
        """
        Set map tick arrays in longitude and latitude.

        lon_axis -- list containing longitude tick mark values.
        lat_axis -- list containing latitude tick mark values.
        """

        if not (isinstance(lon_axis, list) and isinstance(lat_axis, list)):
            raise ValueError('Invalid longitude/latitude axis array')

        self.lon_axis = [float(b) for b in lon_axis]
        self.lat_axis = [float(b) for b in lat_axis]

    def setProjection(self, projection):
        """
        Override default projection type.

        projection -- string giving projection type
        """

        self.projection = projection

    # --------------------------------------------------------
    def drawBase(self, caption, fontsize=10, boarder_col="white", sea_col="#444444", land_col="#bbbbbb", grid_col="white"):
        """
        Set up map projection
        Draw basic map layout including coastlines and boundaries
        Draw lat-long grid
        Set plot title from filename
        """

        # Cylindrical projection (default)
        if self.projection == 'cyl':
            a = np.linspace(self.lat_range[0], self.lat_range[1],4)

            self.m = Basemap(llcrnrlon=self.lon_range[0], llcrnrlat=self.lat_range[0],
                             urcrnrlon=self.lon_range[1], urcrnrlat=self.lat_range[1],
                             projection=self.projection, lat_1=a[1], lat_2=a[2], lon_0=0.,
                             resolution='l', area_thresh=1000.)

        # North Polar Stereographic
        elif self.projection == 'npstere':
            self.m = Basemap(projection=self.projection, boundinglat=self.lat_range[0], lon_0=self.lon_range[0], resolution='l')

        # South Polar Stereographic
        elif self.projection == 'spstere':
            self.m = Basemap(projection=self.projection, boundinglat=self.lat_range[1], lon_0=self.lon_range[0], resolution='l')

        else:
            exit('Unsupported projection! Try cyl|npstere|spstere')

        self.m.drawcoastlines(color=boarder_col, linewidth=0.6, zorder=14)
        self.m.drawcountries(color=boarder_col, zorder=14)
        self.m.drawmapboundary(fill_color=sea_col)
        self.m.fillcontinents(color=land_col, lake_color=sea_col)
        self.m.drawparallels(self.lat_axis, linewidth=0.3, color=grid_col, labels=[1, 0, 0, 1], zorder=14, fontsize=5)
        self.m.drawmeridians(self.lon_axis, linewidth=0.3, color=grid_col, labels=[1, 0, 0, 1], zorder=14, fontsize=5)

        self.ax.set_title(caption, fontsize=fontsize)
    # --------------------------------------------------------
    def zoneLoad(self, files):
        """
        Load gepgraphic zones from list of ESRI shapefiles
        files -- list containing ESRI shapefiles
        """

        self.patches = []

        if not (isinstance(files, list)):
            raise Exception('invalid list of shapefiles')

        for shapefile in files:

            # read ESRI shapefile into GeoPandas object
            shape = gpd.GeoDataFrame.from_file(shapefile)

            for poly in shape.geometry:
                if poly.geom_type == 'Polygon':
                    mpoly = transform(self.m, poly)
                    self.patches.append(PolygonPatch(mpoly))
                elif poly.geom_type == 'MultiPolygon':
                    for subpoly in poly:
                        mpoly = transform(self.m, subpoly)
                        self.patches.append(PolygonPatch(mpoly))

    def zoneColour(self, colours):
        """
        Set display colours for defined ESRI shapes
        colours -- list containing HTML colour names
        """

        self.colours = colours

        if not (isinstance(self.colours, list)):
            raise Exception('Invalid list of zone colours')

        pc = PatchCollection(self.patches, match_original=True)
        pc.set_facecolor(self.colours)
        pc.set_edgecolor('none')
        pc.set_alpha(0.5)
        pc.set_linewidth(0.5)
        pc.set_zorder(20)

        sq = self.ax.add_collection(pc)

    def zoneLines(self, edgecolour='black'):        #was 'red'
        """
        Set boundary colour for defined ESRI shapes
        edgecolour -- HTML colour name for boundary
        """

        pc2 = PatchCollection(self.patches, match_original=True)
        pc2.set_facecolor('none')
        pc2.set_edgecolor(edgecolour)
        pc2.set_alpha(0.5) #5.0
        pc2.set_linewidth(0.5)
        pc2.set_zorder(25) # 500

        sq2 = self.ax.add_collection(pc2)

    # --------------------------------------------------------
    def setColormap(self, colormap='rainbow'):
        """
        Set colourmap with existing normalisation
        colormap -- Matplotlib colourmap name
        """
        self.colormap = getattr(cm, colormap)

    def drawSolid(self, column, color='blue', zorder=6):
        """
        Draw solid shape showing extent of conc > 0.0
        color -- HTML colour
        """
        self.solid = True

        mesh = self.name.data[column]
        mesh1 = mesh.loc[mesh > 0.0]

        mesh2 = mesh1.unstack(level=1)
        mesh2 = mesh2.fillna(0)

        lons = mesh2.index.get_level_values('Longitude')
        lats = mesh2.columns

        mesh2 = mesh2.transpose()

        mesh2[mesh2 > 0] = 1.0
        mesh3 = mesh2.mask(mesh2 < 1.0) # Changed by Teri 03/05/2018

        x,y = self.m(lons, lats)

        cmap = matplotlib.colors.ListedColormap([color])
        norm = matplotlib.colors.LogNorm(vmin=0.99, vmax=1.0, clip=False)

        self.m.pcolormesh(x, y, mesh3, norm=norm, cmap=cmap, zorder=zorder, alpha=0.6)


    def drawMesh(self, column, zorder=6):
        """
        Draw data column values on map
        Add colourbar to plot where plot is not solid type
        """
        mesh = self.name.data[column]
        mesh1 = mesh.loc[mesh > 0.0]

        mesh2 = mesh1.unstack(level=1)
        mesh2 = mesh2.fillna(0)

        lons = mesh2.index.get_level_values('Longitude')
        lats = mesh2.columns

        mesh2 = mesh2.transpose()

        lons2, lats2 = np.meshgrid(lons, lats)

        # -- DEBUG --
        # Check for data straddling longitude 180 meridian
        # Split mesh into two subplots

#         lonsA = [x <= 180 for x in lons]
#         print lonsA
#         if np.any(lonsA):
#             segE = mesh2.iloc[:,lonsA]
#             lonsE = segE.columns
#             latsE = segE.index.get_level_values('Latitude')
#             lonsE2, latsE2 = np.meshgrid(lonsE, latsE)
#             print 'Plotting segE...'
#             try:
#                 pc1 = self.m.pcolormesh(lonsE2, latsE2, segE, latlon=True, cmap=self.colormap, norm=self.norm, zorder=zorder)
#             except IndexError:
#                 pass
#
#             segW = mesh2.iloc[:,[not a for a in lonsA]]
#             print segW
#             lonsW = segW.columns
#             latsW = segW.index.get_level_values('Latitude')
#             lonsW2, latsW2 = np.meshgrid(lonsW, latsW)
# #            print lonsW2
#             print 'Plotting segW...'
#             try:
#                 pc2 = self.m.pcolormesh(lonsW2, latsW2, segW, latlon=True, cmap=self.colormap, norm=self.norm, zorder=30)
#             except IndexError:
#                 pass
#
#             if not self.solid:
#                 self.fig.colorbar(pc2, label=r'Concentration (g s/m$^3$)', shrink=0.5)
#
#         # -- END DEBUG --
#
#         else:

            # Plotting entire input grid
#            print lons2
        pc = self.m.pcolormesh(lons2, lats2, mesh2, latlon=True, cmap=self.colormap, norm=self.norm, zorder=zorder)

        if not self.solid:
            self.fig.colorbar(pc, label=r'Concentration (g s/m$^3$)', shrink=0.5)

    # --------------------------------------------------------
    def addTimestamp(self):
        """
        Add timestamp to plot
        """
        self.fig.text(0.4, 0.15, self.column, color='white', transform=self.ax.transAxes)

    def addMarker(self, lon, lat):
        """
        Add marker to plot at station coordinates
        lon -- station longitude
        lat -- station latitude
        """
        x, y = self.m(lon, lat)
        self.m.plot(x, y, 'kx', markersize=4, zorder=15)

    def addlogo(self, logofile, heightjump):
        #logo = plt.imread(logofile)
        #self.ax.imshow(logo, aspect='auto', extent=(0.4, 0.6, .5, .7), zorder=-1)

        im = Image.open(logofile)
        height = im.size[1]
        im = np.array(im).astype(np.float) / 255
        self.fig.figimage(im, self.fig.bbox.xmin + heightjump, self.fig.bbox.ymin+100)

    def saveFile(self, filename=None):
        """
        Save plot output file
        filename -- output file including type extension
        """
        if filename is None:
            filename = self.filename

        if self.outdir:
            filename = os.path.join(self.outdir, filename)

        print 'Creating plot file: {}'.format(filename)
        self.fig.savefig(filename, dpi=300)

    # --------------------------------------------------------
