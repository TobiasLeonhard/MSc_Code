#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
error_propagation_calculations.py

Description:
This module provides functions to estimate error propagation in DTM-derived analyses.
It implements covariance models (exponential), calculates standard error of the mean for spatial windows, and evaluates cross-covariance between different analysis scales.
These utilities support uncertainty quantification for topographic position index calculations and hummock mapping validation.

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-14
Version: 1.0
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment_hum_prj import *
from config.environment import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def calculate_systematic_covariance_exponential_model(dist_matrix: npt.NDArray, error_sys: float, corr_length: float) -> npt.NDArray:
    """
    Calcualtes the covariance using an exponential covariance model:
        C(h) = (sigma_sys^2) * exp(-d / L)
    Args:
        dist_matrix - npt.NDArray: Distance matrix
        error_sys - float: Systematic error
        error_nug - float: Noise error
        corr_length -  float: Correlation length
    Returns:
        covariance - float: Covariance between point 1 and point 2
    """
    if corr_length == 0:
        covariance_matrix = np.where(dist_matrix == 0, error_sys**2, 0)
    else:
        covariance_matrix = (error_sys**2) * np.exp(-dist_matrix / np.absolute(corr_length))
    return covariance_matrix

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def calculate_standard_error_of_mean(points: npt.NDArray, covariance_model: str, error_sys: float, error_nug: float, corr_length: float) -> float:
    """
    Calculates the standard error of the mean using a defined covariance model.

    Args:
        points - npt.NDArray: Points to use for the calculation.
        covariance_model - str: Name of the covariance model to use.
        error_sys - float: Systematic error
        error_nug - float: Noise error
        corr_length -  float: Correlation length
    """
    enabled_models = ["exponential_model"]
    if not covariance_model in enabled_models:
        raise ValueError(f"Requested undefined model: {covariance_model}")

    num_pts = len(points)

    # Calcualte distances
    dist_matrix = squareform(pdist(points))

    # Calculate systematic covariance
    if covariance_model == "exponential_model":
        cov_matrix = calculate_systematic_covariance_exponential_model(
            dist_matrix = dist_matrix,
            error_sys = error_sys,
            corr_length = corr_length
            )
    else:
         raise ValueError(f"Requested undefined model: {covariance_model}")

    # Add nugget effect to the diagonal (where distance is 0)
    cov_matrix += np.eye(num_pts) * (error_nug**2)

    # SEM = sqrt( sum(all_covariances) / n^2 )
    sem = np.sqrt(np.sum(cov_matrix) / (num_pts**2))
    return sem

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def calculate_covariance_between_two_windows(points_a: npt.NDArray, points_b: npt.NDArray, covariance_model: str, error_sys: float, error_nug: float, corr_length: float) -> float:
    """
    Calculates the covariance between two different window averages.
    Args:
        points_a - npt.NDArray: Points of window A.
        points_b - npt.NDArray: Points of window A.
        covariance_model - str: Name of the covariance model to use.
        error_sys - float: Systematic error
        error_nug - float: Noise error
        corr_length -  float: Correlation length
    Returns:
        covariance -  float: Covariance between A and B
    """
    enabled_models = ["exponential_model"]
    if not covariance_model in enabled_models:
        raise ValueError(f"Requested undefined model: {covariance_model}")

    # Calculate cross-distances between Window A and Window B
    dist_matrix = cdist(points_a, points_b)

    # Systematic part
    if covariance_model == "exponential_model":
        cov_matrix = calculate_systematic_covariance_exponential_model(
            dist_matrix = dist_matrix,
            error_sys = error_sys,
            corr_length = corr_length
            )
    else:
         raise ValueError(f"Requested undefined model: {covariance_model}")

    # Add nugget part: Only where the points are the exact same physical location
    # Since Window A is inside Window B, dist == 0 identifies overlapping pixels
    cov_matrix[dist_matrix == 0] += (error_nug**2)

    covariance = np.sum(cov_matrix) / (len(points_a) * len(points_b))
    return covariance

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def get_grid_points(size: int, resolution: float):
    """
    Helper to generate grid points for a given window size.
    Args:
        size - int: Size of the window
        resolution - float: Raster resolution
    Returns:
        window - npt.NDArray: Window
    """
    radius = size // 2
    x = np.linspace(-radius * resolution, radius * resolution, size)
    y = np.linspace(-radius * resolution, radius * resolution, size)
    window = np.array(np.meshgrid(x, y)).T.reshape(-1, 2)
    return window

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def calculate_standard_error_of_mean_for_different_windows(windows: list, resolution: float, covariance_model: str, error_sys: float, error_nug: float, corr_length: float) -> Tuple[dict, float]:
    """
    Function that calculates the standard error of the mean for different window sizes and returns them as a dictionary
    Args:
        windows - list: List of window sizes
        resolution - float: Resoltion to scale grid distances
        covariance_model - str: Name of the covariance model to use.
        error_sys - float: Systematic error
        error_nug - float: Noise error
        corr_length -  float: Correlation length

    Returns:
        sems - dict: Dictionary containing the standard error of the mean for each window
        cov_between_windows - float: Covariance between the two windows
    """
    if len(windows) != 2:
        raise ValueError("Two window sizes are needed")

    sems = {}
    for size in windows:
        if size < 0:
            raise ValueError("Size must be positve!")
        if not isinstance(size, int):
            raise ValueError("Size must be an integer!")
        if size % 2 != 1:
            raise ValueError("Size must be an odd number!")

        # Generate grid
        grid_points = get_grid_points(
            size = size,
            resolution = resolution
            )

        sems[f"Window {size}x{size}"] = calculate_standard_error_of_mean(
            points = grid_points,
            covariance_model =covariance_model,
            error_sys = error_sys,
            error_nug = error_nug,
            corr_length = corr_length
            )

    grid_a = get_grid_points(
            size = windows[0],
            resolution = resolution
            )
    grid_b = get_grid_points(
            size = windows[1],
            resolution = resolution
            )
    cov_between_windows = calculate_covariance_between_two_windows(
        points_a = grid_a,
        points_b = grid_b,
        covariance_model =covariance_model,
        error_sys = error_sys,
        error_nug = error_nug,
        corr_length = corr_length
        )
    return sems, cov_between_windows

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
