module load python/gcc/27
module load gdal
module load geos
module load spatialindex/1.8.5
. /data/name/Python/venv.geo/bin/activate
export LD_LIBRARY_PATH="/cm/shared/apps/geos/3.6.1/lib:"$LD_LIBRARY_PATH
export GEOS_DIR="/cm/shared/apps/geos/3.6.1/"
export SPATIALINDEX_C_LIBRARY="/cm/shared/apps/spatialindex/1.8.5/lib/libspatialindex_c.so"
