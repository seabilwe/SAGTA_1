import math

from qgis.core import *
from qgis.gui import *

from qgis.PyQt.QtCore import *

# ---------------------------------------------------------------------------
# Grid interval per print scale (degrees).
#
# KEEP IN SYNC with GRID_INTERVAL_BANDS in snapping_expression.py and in the
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
                                   # (z_sa / z_global_thematic multiply this value,
                                   #  so it must stay 4' for those projects)
)

# "Round" intervals used for any other scale, so the grid never collapses
# into a dense mesh when the layout is zoomed to an unlisted scale.
NICE_INTERVALS = (5 / 3600, 10 / 3600, 15 / 3600, 30 / 3600,
                  1 / 60, 2 / 60, 4 / 60)
TARGET_CELL_MM = 40  # aim for grid cells of at least ~40 mm on paper
METRES_PER_DEGREE = 110574  # length of one degree of latitude


def grid_interval_degrees(map_scale):
    """Returns the grid interval (decimal degrees) for a print scale."""
    map_scale = float(map_scale)
    for lower, upper, interval in GRID_INTERVAL_BANDS:
        if lower <= map_scale < upper:
            return interval

    # Unlisted scale: smallest round interval giving cells >= TARGET_CELL_MM
    min_cell_degrees = (TARGET_CELL_MM / 1000 * map_scale) / METRES_PER_DEGREE
    for interval in NICE_INTERVALS:
        if interval >= min_cell_degrees:
            return interval
    return NICE_INTERVALS[-1]


@qgsfunction(args='auto', group='sagta')
def get_grid_interval(map_scale, feature, parent):
    """Calculates the grid interval.
    :param map_scale: The map scale e.g. 50 000
    :type map_scale: float

    :return: grid interval in decimal degrees
    :rtype: float
    """
    return grid_interval_degrees(map_scale)


@qgsfunction(args='auto', group='sagta')
def get_grid_label(
        map_width,
        extent_min,
        interval_width,
        current_grid_value,
        use_letters,
        reversed,
        map_scale,
        axis,
        print_layout,
        print_size,
        feature,
        parent,
        context
):
    """Determines the grid reference label for a grid cell.

    Cells are counted between grid lines from the map edge, so the label works
    at every scale, page size and latitude, and partial cells at the edges get
    their own label in sequence:
      * numbers (1, 2, 3 ...) are counted from the minimum edge (left)
      * letters (A, B, C ...) are counted from the maximum edge (top) when
        ``reversed`` is True
      * partial edge cells with less than EDGE_MIN_FRACTION visible are skipped

    :param map_width: Width (or height, for the y-axis) of the map extent in degrees
    :type map_width: float

    :param extent_min: Minimum coordinate value for the extent
    :type extent_min: float

    :param interval_width: Width of each grid cell in degrees
    :type interval_width: float

    :param current_grid_value: Coordinate of the grid annotation being labelled
                               (the cell centre, as the label grid is offset by
                               half an interval)
    :type current_grid_value: float

    :param use_letters: If set to True, alphabetic chars will be used
    :type use_letters: boolean

    :param reversed: Count from the maximum edge (top) instead of the minimum edge
    :type reversed: boolean

    The remaining parameters (map_scale, axis, print_layout, print_size) are
    kept so existing project expressions keep working; they are no longer
    needed to work out the label.

    :return: Alphabetic label for rows, numeric label for columns
    :rtype: str
    """
    interval_width = float(interval_width)
    if not interval_width or interval_width <= 0:
        return ''

    lower = float(extent_min)
    upper = lower + float(map_width)
    value = float(current_grid_value)

    # Cell k spans [k * interval, (k + 1) * interval] (grid lines sit on whole
    # multiples of the interval). Partial cells at the map edges count as cells,
    # unless less than EDGE_MIN_FRACTION of the cell is visible (a sliver).
    cell = _grid_index(value, interval_width)
    if _visible_fraction(cell, lower, upper, interval_width) < EDGE_MIN_FRACTION:
        return ''

    if reversed:
        # Count from the top (maximum) edge: A = top cell
        first = _grid_index(upper, interval_width, upper_edge=True)
        if _visible_fraction(first, lower, upper, interval_width) < EDGE_MIN_FRACTION:
            first -= 1
        index = first - cell
    else:
        # Count from the left (minimum) edge: 1 = left cell
        first = _grid_index(lower, interval_width)
        if _visible_fraction(first, lower, upper, interval_width) < EDGE_MIN_FRACTION:
            first += 1
        index = cell - first

    if index < 0:
        return ''
    if use_letters:
        return index_to_letters(index)
    return str(index + 1)


EDGE_MIN_FRACTION = 0.1  # partial edge cells narrower than 10% of a cell get no label


def _grid_index(value, interval, upper_edge=False):
    """Index of the grid cell containing value (a value exactly on a grid line
    belongs to the cell above it, or below it when upper_edge is True)."""
    q = value / interval
    nearest = round(q)
    if abs(q - nearest) < 1e-6:
        return int(nearest) - 1 if upper_edge else int(nearest)
    return int(math.floor(q))


def _visible_fraction(cell, lower, upper, interval):
    """Share of grid cell `cell` that falls inside [lower, upper]."""
    start = cell * interval
    end = start + interval
    return max(0.0, min(end, upper) - max(start, lower)) / interval


def index_to_letters(index):
    """0 -> A, 25 -> Z, 26 -> AA, 27 -> AB ..."""
    letters = ''
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters
