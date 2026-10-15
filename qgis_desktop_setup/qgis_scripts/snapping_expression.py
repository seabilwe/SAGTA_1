import math

from qgis.core import *
from qgis.gui import *

from qgis.PyQt.QtCore import *

# ---------------------------------------------------------------------------
# Grid interval per print scale (degrees).
#
# KEEP IN SYNC with GRID_INTERVAL_BANDS in custom_grid_label.py and in the
# QGIS Server plugins (custom_grid_label/customgridlabel/gridlabelfunctions.py
# and SnappingExpression/__init__.py).
#
# (min scale inclusive, max scale exclusive, interval in degrees)
# ---------------------------------------------------------------------------
GRID_INTERVAL_BANDS = (
    (4750, 5250, 10 / 3600),       # 1:5 000   -> 10"
    (9500, 10500, 15 / 3600),      # 1:10 000  -> 15"
    (23000, 27000, 1 / 60),        # 1:25 000  -> 1'
    (48000, 52000, 1 / 60),        # 1:50 000  -> 1'
    (98000, 110000, 2 / 60),       # 1:100 000 -> 2'
    (140000, math.inf, 4 / 60),    # 1:150 000 and smaller scales -> 4'
)
NICE_INTERVALS = (5 / 3600, 10 / 3600, 15 / 3600, 30 / 3600,
                  1 / 60, 2 / 60, 4 / 60)
TARGET_CELL_MM = 40
METRES_PER_DEGREE = 110574


def grid_interval_degrees(map_scale):
    """Returns the grid interval (decimal degrees) for a print scale."""
    map_scale = float(map_scale)
    for lower, upper, interval in GRID_INTERVAL_BANDS:
        if lower <= map_scale < upper:
            return interval
    min_cell_degrees = (TARGET_CELL_MM / 1000 * map_scale) / METRES_PER_DEGREE
    for interval in NICE_INTERVALS:
        if interval >= min_cell_degrees:
            return interval
    return NICE_INTERVALS[-1]


@qgsfunction(args='auto', group='sagta')
def snap_x_axis(x_min, map_scale, map_crs, geo_crs, feature, parent, context):
    """Snaps the left edge of the map to the nearest grid line.

    Used as the data-defined "X min" of the layout map, e.g.
    snap_x_axis(xmin(transform(@map_extent, @map_crs, 'EPSG:4326')),
                @map_scale, @map_crs, 'EPSG:4326')

    :param x_min: Left edge of the map extent in geographic coordinates
    :type x_min: float

    :param map_scale: The scale of the current map
    :type map_scale: float

    :param map_crs: Map coordinate system (e.g. EPSG:3857)
    :type map_crs: str

    :param geo_crs: Geographic coordinate system of x_min (e.g. EPSG:4326)
    :type geo_crs: str

    :return: The snapped x-coordinate in the map CRS
    :rtype: float
    """
    snapped_lon = snap_to_grid(x_min, map_scale)
    _, centre_lat = map_centre(context, map_crs, geo_crs)
    x, _ = transform_coordinates(snapped_lon, centre_lat, geo_crs, map_crs)
    return x


@qgsfunction(args='auto', group='sagta')
def snap_y_axis(y_max, map_scale, map_crs, geo_crs, feature, parent, context):
    """Snaps the top edge of the map to the nearest grid line.

    Used as the data-defined "Y max" of the layout map, e.g.
    snap_y_axis(y_max(transform(@map_extent, @map_crs, 'EPSG:4326')),
                @map_scale, @map_crs, 'EPSG:4326')

    :param y_max: Top edge of the map extent in geographic coordinates
    :type y_max: float

    :param map_scale: The scale of the current map
    :type map_scale: float

    :param map_crs: Map coordinate system (e.g. EPSG:3857)
    :type map_crs: str

    :param geo_crs: Geographic coordinate system of y_max (e.g. EPSG:4326)
    :type geo_crs: str

    :return: The snapped y-coordinate in the map CRS
    :rtype: float
    """
    snapped_lat = snap_to_grid(y_max, map_scale)
    centre_lon, _ = map_centre(context, map_crs, geo_crs)
    _, y = transform_coordinates(centre_lon, snapped_lat, geo_crs, map_crs)
    return y


def snap_to_grid(value, map_scale):
    """Rounds a coordinate (decimal degrees) to the nearest grid line."""
    interval = grid_interval_degrees(map_scale)
    return round(math.floor(float(value) / interval + 0.5) * interval, 10)


def map_centre(context, map_crs, geo_crs):
    """Centre of the current map extent in geographic coordinates.

    Only used to pick the other coordinate for the CRS transform; falls back
    to 0, 0 if the extent is not available.
    """
    try:
        extent = context.variable('map_extent') if context else None
        if extent:
            centre = extent.centroid().asPoint()
            return transform_coordinates(centre.x(), centre.y(), map_crs, geo_crs)
    except Exception:
        pass
    return 0.0, 0.0


def transform_coordinates(x, y, curr_crs, target_crs):
    """Transforms coordinates from one coordinate system to another.

    :param curr_crs: Current coordinate system (auth id string or QgsCoordinateReferenceSystem)
    :param target_crs: Target coordinate system (auth id string or QgsCoordinateReferenceSystem)

    :return: X- and Y-coordinates
    :rtype: float
    """
    if not isinstance(curr_crs, QgsCoordinateReferenceSystem):
        curr_crs = QgsCoordinateReferenceSystem(curr_crs)
    if not isinstance(target_crs, QgsCoordinateReferenceSystem):
        target_crs = QgsCoordinateReferenceSystem(target_crs)

    transform_context = QgsProject.instance().transformContext()
    xform = QgsCoordinateTransform(curr_crs, target_crs, transform_context)
    pt = xform.transform(QgsPointXY(float(x), float(y)))
    return pt.x(), pt.y()
