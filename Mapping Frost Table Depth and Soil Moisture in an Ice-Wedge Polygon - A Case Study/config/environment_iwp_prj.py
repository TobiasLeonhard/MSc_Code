#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
environment_iwp_prj.py

Description:
This configuration file establishes the computational environment for the ice-wedge polygon study.
It imports required Python libraries including rioxarray for spatial data processing and scikit-posthocs for statistical testing, and defines project directory paths for input data, analysis results, maps, and manual validation layers.
The configuration ensures consistent file access and environment setup across all analysis scripts in the ice-wedge polygon workflow.

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-14
"""
# ==================================================================================================== #
# Standard Libraries
# ---------------------------------------------------------------------------------------------------- #
# Sys
import sys
# ---------------------------------------------------------------------------------------------------- #
# Pathlib
from pathlib import Path
# ---------------------------------------------------------------------------------------------------- #
# Shutil
import shutil
# ---------------------------------------------------------------------------------------------------- #

# ==================================================================================================== #
# Third-Party Libraries
# ---------------------------------------------------------------------------------------------------- #
# Rioxarray
import rioxarray
# ---------------------------------------------------------------------------------------------------- #
# Scikit posthocs
import scikit_posthocs as sp
# ---------------------------------------------------------------------------------------------------- #
# ==================================================================================================== #

# ==================================================================================================== #
# Defining Paths and more
# ---------------------------------------------------------------------------------------------------- #
if "project_path" not in globals():
    coding_folder = Path(__file__).resolve().parent.parent
    data_folder = coding_folder / "data"
    results_folder = coding_folder / "results"
    final_maps_folder = coding_folder / "map_generation" / "Final Maps"
    dtm_calculations_folder =  results_folder / "dtm_calculations"
    manual_input_folder = coding_folder / "manual_input_data"

    # Create Folders
    data_folder.mkdir(exist_ok = True)
    final_maps_folder.mkdir(exist_ok = True, parents = True)
    results_folder.mkdir(exist_ok = True)
    dtm_calculations_folder.mkdir(exist_ok = True)

# ==================================================================================================== #
