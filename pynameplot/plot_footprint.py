#! /usr/bin/env python

import os
import argparse
import tempfile
import shutil
import calendar
from datetime import datetime

from namereader import drawmap
from namereader import name
from namereader import namesum


class TemporaryDirectory(object):
    """Context manager for tempfile.mkdtemp() so it's usable with "with" statement."""
    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)

def main():

    parser = argparse.ArgumentParser(prog='plot_footprint', description='Plot NAME concentration files on world map')
    parser.add_argument('-i', '--infiles', nargs='+', required=True, help="NAME output files to plot")
    parser.add_argument('-o', '--outputdir', nargs='?', required=True, help="Plot output directory")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-t', '--time', nargs='?', help='Specific datetime to plot (YYYY-MM-DD HH:MM UTC)')
    group.add_argument('-d', '--day', nargs='?', help='Plot summary of this day')
    group.add_argument('-w', '--week', nargs='?', help='Plot summary of this week')
    group.add_argument('-m', '--month', nargs='?', help='Plot summary of this month')
    group.add_argument('-y', '--year', nargs='?', help='Plot summary of this year')
    group.add_argument('-a', '--all', action='store_true', default=False, help='Plot summary of all files')

    args = parser.parse_args()

    print args

    if len(args.infiles) == 1:
        n = name.Name(args.infiles[0])
        if args.time:
            # draw map for single timestamp
            column = args.time
            n.column = column
            drawmap.drawMap(n, column, outdir=args.outputdir)
        else:
            # draw maps for all timestamps in file
            for column in n.timestamps:
                print n.timestamps
                n.column = column
                drawmap.drawMap(n, column, outdir=args.outputdir)

    else:
        # Copy files to a temporary directory
        with TemporaryDirectory() as tmpdir:
            for f in args.infiles:
                shutil.copy(f, tmpdir)

            s = namesum.Sum(tmpdir)
            column = 'total'

            if args.day:
                # draw summed map for day
                s.sumDay(args.day)

                caption = "{} {} {} {}: {}{}{} day sum".format(s.runname, s.averaging, s.altitude, s.direction, s.year,
                                                               s.month, s.day)
                outfile = "{}_{}{}{}_daily.png".format(s.runname, s.year, s.month, s.day)

                drawmap.drawMap(s, column, caption=caption, outfile=outfile, outdir=args.outputdir)

            elif args.week:
                # draw summed map for week
                s.sumWeek(args.week)

                caption = "{} {} {} {}: {} week {} sum".format(s.runname, s.averaging, s.altitude, s.direction, s.year,
                                                               args.week)
                outfile = "{}_{}{}_weekly.png".format(s.runname, s.year, args.week.zfill(2))

                drawmap.drawMap(s, column, caption=caption, outfile=outfile, outdir=args.outputdir)

            elif args.month:
                # draw summed map for month
                s.sumMonth(args.month)

                caption = "{} {} {} {}: {} {} sum".format(s.runname, s.averaging, s.altitude, s.direction, s.year,
                                                          calendar.month_name[int(args.month)])
                outfile = "{}_{}{}_monthly.png".format(s.runname, s.year, args.month.zfill(2))
                drawmap.drawMap(s, column, caption=caption, outfile=outfile, outdir=args.outputdir)

            elif args.year:
                # draw summed map for year
                s.sumYear(args.year)

                caption = "{} {} {} {}: {} year sum".format(s.runname, s.averaging, s.altitude, s.direction, args.year)
                outfile = "{}_{}_yearly.png".format(s.runname, args.year)

                drawmap.drawMap(s, column, outdir=args.outputdir)

            elif args.all:
                # draw summed map for entire directory
                s.sumAll()

                caption = "{} {} {} {}: Summed".format(s.runname, s.averaging, s.altitude, s.direction)
                outfile = "{}_summed_all.png".format(s.runname)
                drawmap.drawMap(s, column, outdir=args.outputdir)

            else:
                # draw maps for all timestamps and files in directory
                allfiles = sorted(s.fs.getAll())

                for f in allfiles:
                    n = name.Name(f)
                    for column in n.timestamps:
                        n.column = column
                        drawmap.drawMap(n, column, outdir=args.outputdir)

        # End with so tempdir is deleted


if __main__ == "__main__":
    main()