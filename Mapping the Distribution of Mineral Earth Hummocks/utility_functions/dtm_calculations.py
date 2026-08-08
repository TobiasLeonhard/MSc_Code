#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
utils_dtm_calculations.py

Functions for DTM calculations.

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-06
Version: 1.0
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def get_mean_elevation(input_dtm: Path, window_length: int) -> Path:
    """
    Calculates or generates the mean elevation of the input_dtm and stores the output as a tif file.
    Args:
        input_dtm - Path: Path of the dtm that is used to calculate the mean elevation.
        window_length - int: Filter size e.g. window size in pixels. The window is window_length * window_length
    Returns:
        output_path - Path: Path to the generated mean elevation file.
    """
    if window_length % 2 == 0:
        raise ValueError("window_length musst be odd.")

    if not input_dtm.exists():
        raise FileNotFoundError("Could not find input file.")

    output_path = dtm_calculations_folder / Path(f"{input_dtm.stem}_meaned_over_{window_length}px").with_suffix(".tif")
    output_path.parent.mkdir(parents = True, exist_ok = True)

    if not output_path.exists():
        wbt.mean_filter(
            input_dtm,
            output_path,
            filterx = window_length,
            filtery = window_length
            )
    return output_path

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def get_smoothed_diff(input_dtm: Path, window_length_1: int, window_length_2: int) -> Path:
    """
    Calculates or generates the difference from elevation using two smoothed dtms.
    Args:
        input_dtm - Path: Path of the dtm that is used to calculate the mean elevation.
        window_length_1 - int: Filter size e.g. window size in pixels. The window is window_length * window_length
        window_length_2 - int: Filter size e.g. window size in pixels. The window is window_length * window_length
    Returns:
        output_path - Path: Path to the generated mean elevation file.
    """
    if window_length_1 % 2 == 0:
        raise ValueError("window_length_1 musst be odd.")
    if window_length_2 % 2 == 0:
        raise ValueError("window_length_2 musst be odd.")

    if window_length_1 == window_length_2:
        raise ValueError("window_length_1 and window_length_2 musst be different.")

    if window_length_1 > window_length_2:
        print("Warning - get_smoothed_diff(): window_length_1 is bigger than window_length_2")
    if not input_dtm.exists():
        raise FileNotFoundError("Could not find input file.")

    output_path = dtm_calculations_folder / Path(f"{input_dtm.stem}_smoothed_diff_with_window_lengths_of_{window_length_1}px_and_{window_length_2}px").with_suffix(".tif")
    output_path.parent.mkdir(parents = True, exist_ok = True)

    if not output_path.exists():
        smoothed_dtm_1 = get_mean_elevation(
            input_dtm = input_dtm,
            window_length = window_length_1
            )
        smoothed_dtm_2 = get_mean_elevation(
            input_dtm = input_dtm,
            window_length = window_length_2
            )
        wbt.subtract(
            smoothed_dtm_1,
            smoothed_dtm_2,
            output_path
            )

    return output_path

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def get_thresholded_map(input_dtm: Path, threshold: np.floating, threshold_type: str) -> Path:
    """
    Calculates or gets a thresholded map of the input_dtm depending on the threshold and threshold_type
    Args:
        input_dtm - Path: Path of the dtm that is thresholded
        threshold - float: Threshold value
        threshold_type - str: Type, for example "greater than"
    Returns:
        output_path - Path: Path to the generated mean elevation file.
    """
    if threshold_type in ["gt", "greater than"]:
        threshold_type_str = "gt"
    else:
        raise ValueError(f"{threshold_type} not recognized")

    threshold_str = str(threshold).replace(".", "p")
    output_path =  dtm_calculations_folder / Path(f"{input_dtm.stem}_{threshold_type_str}_{threshold_str}").with_suffix(".tif")
    output_path.parent.mkdir(parents = True, exist_ok = True)

    if not output_path.exists():
        if threshold_type_str == "gt":
            wbt.greater_than(
                input1 = input_dtm,
                output = output_path,
                input2 = threshold
                )
    return output_path

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def get_slope_map(input_dtm: Path, units: str, z_factor: float) -> Path:
    """
    Calculates or gets a slope map of the input_dtm in the wanted units and z factor
    Args:
        input_dtm - Path: Path of the dtm that is sloped
        units - str: Unit type. One of 'degrees', 'radians', 'percent'
        z_factor - float: Z Factor
    Returns:
        output_path - Path: Path to the generated slope file.
    """
    allowed_units = ["degrees", "radians", "percent"]
    if not units in allowed_units:
        raise ValueError(f"{units} is not accepted, choose one of these options: {allowed_units}!")

    output_path = dtm_calculations_folder / Path(f"{input_dtm.stem}_slope_in_{units}_with_zfactor_{str(z_factor).replace('.', 'p')}").with_suffix(".tif")
    output_path.parent.mkdir(parents = True, exist_ok = True)

    if not output_path.exists():
        wbt.slope(
            input_dtm,
            output_path,
            zfactor = 1,
            units = units
            )

    return output_path

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
