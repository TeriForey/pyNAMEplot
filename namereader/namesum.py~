# Author: Duncan Law-Green (dlg@kyubi.co.uk)
# Copyright 2017 Kyubi Systems
# Licensed under the Apache License, Version 2.0 (see LICENSE)
# ------------------------------------------------------------
# 
# NAMESUM
# 
# Support libraries. Sum NAME geochemical dataframes over a given timespan.
# 

from .name import Name
from .fileset import Fileset


class Sum(Name):
      """
      Class to sum over multiple NAME files
      Generates result in 'total' column
      Extends existing Name class
      """
      
      directory = ''
      files = []
      
      def __init__(self, directory):
            """
            Initialise Sum object
            directory -- input directory path
            """
            
            self.directory = directory
            self.fs = Fileset(directory)

      def sumAll(self):
            """
            Add all NAME files in Fileset
            """

            self.files = sorted(self.fs.getAll())
            self.__addFiles(self.files)

      def sumBetween(self, start, stop):
            """
            Add all NAME files between start and end dates
            start -- start date (YYYYMMDD format)
            stop -- stop date (YYYYMMDD format)
            """

            self.files = sorted(self.fs.between(start, stop))
            self.__addFiles(self.files)

      def sumDay(self, day):
            """
            Add all NAME files for given day 
            day -- date in YYYYMMDD format
            """

            self.files = sorted(self.fs.getDay(day))
            self.__addFiles(self.files)
            
      def sumWeek(self, w):
            """
            Add NAME files for given week number
            w -- ISO-8601 week number
            """

            self.files = sorted(self.fs.weeks[w])
            self.__addFiles(self.files)

      def sumMonth(self, m):
            """
            Add NAME files for given month number
            m -- month number
            """
            
            self.files = sorted(self.fs.months[m])
            self.__addFiles(self.files)

      def sumYear(self, y):
            """
            Add NAME files for given year
            y -- year
            """

            self.files = sorted(self.fs.years[y])
            self.__addFiles(self.files)

      def __addFiles(self, files):
            """
            NAME data add operation method
            Tagged as private method
            files -- list of input NAME files
            """

            print 'Loading: ', files[0]
            n = Name(files[0])
            n.add_all()

            # Load Sum object metadata from first Name file found
            self.runname = n.runname
            self.release = n.release
            self.averaging = n.averaging
            self.duration = n.duration
            self.altitude = n.altitude
            self.direction = n.direction
            self.lon_bounds = n.lon_bounds
            self.lat_bounds = n.lat_bounds
            self.lon_grid = n.lon_grid
            self.lat_grid = n.lat_grid
            self.year = n.year
            self.month = n.month
            self.day = n.day
            
            m = n.trimmed()
            m = m.rename(columns={'subtotal': 'total'})

            for f in files[1::]:
                  print 'Loading: ', f
                  n2 = Name(f)
                  n2.add_all()
                  m2 = n2.trimmed()

                  #m = m.join(m2, how='outer')
                  m = m.combine_first(m2)
                  m = m.fillna(0)

                  m.total = m.total + m.subtotal
                  m = m.drop('subtotal', 1)

            self.data = m
