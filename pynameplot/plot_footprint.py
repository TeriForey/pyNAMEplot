import argparse
import tempfile
import shutil
import calendar

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

    parser.add_argument('-s', '--station', nargs = 2, type=float, required=False,
                        help="Longitude and latitude of the release station")
    parser.add_argument('-p', '--projection', nargs='?', choices=['cyl', 'npstere', 'spstere'], default='cyl',
                        help="Map projection")
    parser.add_argument('-c', '--colormap', nargs='?', default='rainbow', help="matplotlib colour map [%(default)s]")

    args = parser.parse_args()

    plotoptions = {'outdir': args.outputdir}
    if args.station:
        plotoptions['station'] = (args.station[0], args.station[1])
    if args.projection:
        plotoptions['projection'] = args.projection
    if args.colormap:
        plotoptions['colormap'] = args.colormap

    if len(args.infiles) == 1:
        n = name.Name(args.infiles[0])
        if args.time:
            # draw map for single timestamp
            column = args.time
            n.column = column
            drawmap.drawMap(n, column, **plotoptions)
        else:
            # draw maps for all timestamps in file
            for column in n.timestamps:
                print n.timestamps
                n.column = column
                drawmap.drawMap(n, column, **plotoptions)

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

                plotoptions['caption'] = "{} {} {} {}: {}{}{} day sum (UTC)".format(s.runname, s.averaging, s.altitude,
                                                                              s.direction, s.year, s.month, s.day)
                plotoptions['outfile'] = "{}_{}{}{}_daily.png".format(s.runname, s.year, s.month, s.day)

                drawmap.drawMap(s, column, **plotoptions)

            elif args.week:
                # draw summed map for week
                s.sumWeek(args.week)

                plotoptions['caption'] = "{} {} {} {}: {} week {} sum (UTC)".format(s.runname, s.averaging, s.altitude,
                                                                              s.direction, s.year, args.week)
                plotoptions['outfile'] = "{}_{}{}_weekly.png".format(s.runname, s.year, args.week.zfill(2))

                drawmap.drawMap(s, column, **plotoptions)

            elif args.month:
                # draw summed map for month
                s.sumMonth(args.month)

                plotoptions['caption'] = "{} {} {} {}: {} {} sum (UTC)".format(s.runname, s.averaging, s.altitude,
                                                                         s.direction, s.year,
                                                                         calendar.month_name[int(args.month)])
                plotoptions['outfile'] = "{}_{}{}_monthly.png".format(s.runname, s.year, args.month.zfill(2))
                drawmap.drawMap(s, column, **plotoptions)

            elif args.year:
                # draw summed map for year
                s.sumYear(args.year)

                plotoptions['caption'] = "{} {} {} {}: {} year sum (UTC)".format(s.runname, s.averaging, s.altitude,
                                                                           s.direction, args.year)
                plotoptions['outfile'] = "{}_{}_yearly.png".format(s.runname, args.year)

                drawmap.drawMap(s, column, **plotoptions)

            elif args.all:
                # draw summed map for entire directory
                s.sumAll()

                plotoptions['caption'] = "{} {} {} {}: Summed (UTC)".format(s.runname, s.averaging, s.altitude,
                                                                            s.direction)
                plotoptions['outfile'] = "{}_summed_all.png".format(s.runname)
                drawmap.drawMap(s, column, **plotoptions)

            else:
                # draw maps for all timestamps and files in directory
                allfiles = sorted(s.fs.getAll())

                for f in allfiles:
                    n = name.Name(f)
                    for column in n.timestamps:
                        n.column = column
                        drawmap.drawMap(n, column, **plotoptions)

        # End with so tempdir is deleted


if __name__ == "__main__":
    main()
