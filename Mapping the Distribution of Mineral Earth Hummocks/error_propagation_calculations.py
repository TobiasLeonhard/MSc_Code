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
This script estimates the propagation of error in Topographic Position Index calculations used for mineral earth hummock mapping.
It evaluates the standard error of the mean for different analysis window sizes,
incorporates assumed lidar error terms and correlation lengths, and determines the correlation length required to explain the observed TPI variability.
The results provide a statistical basis for assessing the reliability of hummock mapping outputs and the appropriate spatial scales for analysis.

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
parent_folder = Path(__file__).resolve().parent
sys.path.append(str(parent_folder))
from config.environment_hum_prj import *
from config.environment import *
from utility_functions.error_propagation_calculations import calculate_standard_error_of_mean_for_different_windows
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("error_propagation_calculations.py started")
    print("Estimating error propogation in TPI calculations used for hummock mapping.")

    # -------------------------------------------------- #
    # Setup
    resolution = 0.5 # Resolution of the DTM in m
    error_tot = 0.08 # Total error (taken from Intraswath accuracy)
    error_nug = 0.02 # Instrumental noise (assumed, should be relative low for the used lidar)
    error_sys = np.sqrt(error_tot**2 - error_nug**2) # Systematic error calculated from instrumental error and total error

    lower_corr_length_factor = 3

    # Define input list
    input_list = [
        [
            0.011579984799027443, # Standard deviation of the TPI calculated using a 1x1 and 5x5 window
            [1, 5]
            ],
        [
            0.020344803109765053, # Standard deviation of the TPI calculated using a 1x1 and 7x7 window
            [1, 7]
            ],
        [
            0.011579984799027443, # Standard deviation of the TPI calculated using a 3x3 and 5x5 window
            [3, 5]
            ],
        [
            0.020344803109765053, # Standard deviation of the TPI calculated using a 3x3 and 7x7 window
            [3, 7]
            ],
        ]
    for sigma_tpi, window_sizes in input_list:
        print("--------------------------------------------------")
        print(f"Processing window sizes {window_sizes[0]}x{window_sizes[0]} and {window_sizes[1]}x{window_sizes[1]}\n")
        window_1 = f"Window {window_sizes[0]}x{window_sizes[0]}"
        window_2 = f"Window {window_sizes[1]}x{window_sizes[1]}"

        corr_length_factor = lower_corr_length_factor

        # -------------------------------------------------- #
        # Calculating standard error of the mean for the TPI using a realisitc correlation length
        assumed_corr_length = corr_length_factor * resolution
        sems, covariance = calculate_standard_error_of_mean_for_different_windows(
            windows = window_sizes,
            resolution = resolution,
            covariance_model = "exponential_model" ,
            error_sys = error_sys,
            error_nug = error_nug,
            corr_length = assumed_corr_length
            )

        calculated_sem = np.sqrt(np.absolute(sems[window_1]**2 + sems[window_2]**2 - (2 * covariance)))

        # -------------------------------------------------- #
        # Results for a realistic correlation lenght
        print(f"    Results using a realistic correlation lengthof {assumed_corr_length} m:")
        print(f"        Standard Error of the Mean = {calculated_sem} m.\n")

        # -------------------------------------------------- #
        # Finding the approximate correlation length that would explain the standard deviation of the calculate TPI
        step_width = 0.5
        corr_length_factor = lower_corr_length_factor
        while calculated_sem > sigma_tpi:
            old_sem = calculated_sem

            assumed_corr_length = corr_length_factor * resolution
            sems, covariance = calculate_standard_error_of_mean_for_different_windows(
                windows = window_sizes,
                resolution = resolution,
                covariance_model = "exponential_model" ,
                error_sys = error_sys,
                error_nug = error_nug,
                corr_length = assumed_corr_length
                )

            calculated_sem = np.sqrt(np.absolute(sems[window_1]**2 + sems[window_2]**2 - (2 * covariance)))

            corr_length_factor += step_width
            break_length = 1000 * step_width
            if (corr_length_factor * resolution) > break_length:
                print(f"Correlation length over {break_length}, stopped loop.")
                break
        # -------------------------------------------------- #
        # Results for a needed correlation length
        print(f"    Results for calculating a correlation length needed to explain the standard deviation of {sigma_tpi} m found for the used TPI:")
        print(f"        Standard Error of the Mean = {calculated_sem} m for a correlation length of {(corr_length_factor * resolution)} m.")
        print(f"        Standard Error of the Mean = {old_sem} m for a correlation length of {(corr_length_factor * resolution - step_width)} m.\n")

    print("\nerror_propagation_calculations.py finished.")
    print("# ====================================================================================================================================================== #")
