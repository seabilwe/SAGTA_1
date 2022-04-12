import math
import typing
from string import ascii_uppercase

from qgis.core import *
from qgis.gui import *

from qgis.PyQt.QtCore import *

@qgsfunction(args='auto', group='sagta')
def get_grid_interval(map_scale, feature, parent):
    """Calculates the grid interval.
    :param map_scale: The map scale e.g. 50 000
    :type map_scale: float
    
    :return: grid interval
    :rtype: float
    """
    
    current_scale = float(map_scale)
    if map_scale >= 140000:  # 150k
        result = 0.066666666668
    elif 98000 <= map_scale < 110000:  # 100k
        result = 0.033333333334
    elif 48000 <= map_scale < 52000:  # 50k
        result = 0.016666666667
    elif 23000 <= map_scale < 27000:  # 25k
        result = 0.016666666667
    else:
        result = 0.00416666666675
    
    return result

    
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
    """Determines the grid label for the provider grid position.
    :param map_width: Width of the layout
    :type map_width: float
    
    :param extent_min: Minimum coordinate value for the extent
    :type extent_min: float
    
    :param interval_width: Width of each grid
    :type interval_width: float
    
    :param current_grid_value: Index of the current grid to be labelled
    :type current_grid_value: int
    
    :param use_letters: If set to True, alphabetic chars will be used
    :type use_letters: boolean
    
    :param reversed: Reverse labelling order
    :type reversed: boolean
    
    :param map_scale: Scale of the current map (e.g. 50 000)
    :type map_scale: float
    
    :param axis: The used by the layout (this will be x for the y-axis, y for the x-axis)
    :type axis: string
    
    :param print_layout: Landscape or Portrait
    :type print_layout: string
    
    :param print_size: A3 or A4
    :type print_size: string
    
    :return: Returns the label. Alphabetic chars for y-axis, numeric for x-axis
    :rtype: str/int
    """
    
    num_intervals = get_num_intervals(axis, map_scale, print_layout, print_size)  # Number of grid intervals
    current_position = current_grid_value - extent_min  # Label position
    
    for i in range(num_intervals):  # Loops through each of the grids
        interval_start = extent_min + i * interval_width  # Grid start coordinates
        interval_end = extent_min + (i + 1) * interval_width  # Grid end coordinates
        
        # Find the grid block which needs to be labelled
        if interval_start <= current_grid_value < interval_end:
            result = get_choices_label(
                i,
                num_intervals,
                reverse_order=reversed,
                choices=ascii_uppercase if use_letters else None,
            )
            break
    else:  # When the loop ends
        result = 'error'
    
    return result


def get_num_intervals(axis, map_scale, print_layout, print_size):
    """Determines the grid label for the provider grid position.
    :param axis: Axis returned by QGIS
    :type axis: str
    
    :param map_scale: Scale of the current map
    :type map_scale: float
    
    :param print_layout: Landscape or Portrait
    :type print_layout: string
    
    :return: Returns the number of intervals
    :rtype: int
    """
    
    num_intervals = -1
    if print_layout.lower() == 'landscape':
        if print_size.lower() == 'a3':  # A3
            if 23000 <= map_scale < 27000:  # 25k
                if axis == 'x':
                    num_intervals = 3
                else:
                    num_intervals = 5
            elif 48000 <= map_scale < 52000:  # 50k
                if axis == 'x':
                    num_intervals = 5
                else:
                    num_intervals = 10
            elif 98000 <= map_scale < 110000:  # 100k
                if axis == 'x':
                    num_intervals = 5
                else:
                    num_intervals = 10
            elif map_scale >= 140000:  # 150k
                if axis == 'x':
                    num_intervals = 4
                else:
                    num_intervals = 8
        else:  # A4
            if 23000 <= map_scale < 27000:  # 25k
                if axis == 'x':
                    num_intervals = 2
                else:
                    num_intervals = 4
            elif 48000 <= map_scale < 52000:  # 50k
                if axis == 'x':
                    num_intervals = 4
                else:
                    num_intervals = 7
            elif 98000 <= map_scale < 110000:  # 100k
                if axis == 'x':
                    num_intervals = 4
                else:
                    num_intervals = 7
            elif map_scale >= 140000:  # 150k
                if axis == 'x':
                    num_intervals = 3
                else:
                    num_intervals = 6
    else:  # Portrait
        if print_size.lower() == 'a3':  # A3
            if 23000 <= map_scale < 27000:  # 25k
                if axis == 'x':
                    num_intervals = 4
                else:
                    num_intervals = 4
            elif 48000 <= map_scale < 52000:  # 50k
                if axis == 'x':
                    num_intervals = 8
                else:
                    num_intervals = 7
            elif 98000 <= map_scale < 110000:  # 100k
                if axis == 'x':
                    num_intervals = 8
                else:
                    num_intervals = 7
            elif map_scale >= 140000:  # 150k
                if axis == 'x':
                    num_intervals = 6
                else:
                    num_intervals = 5
        else:  # A4
            if 23000 <= map_scale < 27000:  # 25k
                if axis == 'x':
                    num_intervals = 3
                else:
                    num_intervals = 3
            elif 48000 <= map_scale < 52000:  # 50k
                if axis == 'x':
                    num_intervals = 5
                else:
                    num_intervals = 5
            elif 98000 <= map_scale < 110000:  # 100k
                if axis == 'x':
                    num_intervals = 5
                else:
                    num_intervals = 5
            elif map_scale >= 140000:  # 150k
                if axis == 'x':
                    num_intervals = 4
                else:
                    num_intervals = 4
    
    return num_intervals

    
def get_choices_label(
        current_item: int,
        total_items: int,
        reverse_order: typing.Optional[bool] = False,
        choices: typing.Optional[typing.Iterable] = None,
        offset: typing.Optional[int] = 1,
) -> str:
    """Gets the label for the evaluated grid index.
    :current_item: Index of current grid
    :type current_item: int
    
    :param total_items: Total number of grids for the x- or y-axis
    :type total_items: int
    
    :param reverse_order: True if the labelling order should be reversed
    :type reverse_order: boolean
    
    :param choices: If the user provides a list of choices
    :type choices: array
    
    :param offset: Offset set by the user
    :type offset: int
    
    :return: Returns the label. Alphabetic chars for y-axis, numeric for x-axis
    :rtype: str/int
    """
    
    output_values = None
    
    if choices is None:  # x-axis, therefore integer values
        # Increments with one to be sure to include the last grid block case
        possible_outputs = range(total_items + 1)
        output_values = list(possible_outputs)[:total_items + 1]
        
        index = current_item + offset
        
    else:  # y-axis, therefore alphabetical characters
        possible_outputs = choices
        output_values = list(possible_outputs)[:total_items]
        
        list_len = len(output_values)
        index = total_items - current_item - offset  # Reverses the order
    
    return output_values[index]
