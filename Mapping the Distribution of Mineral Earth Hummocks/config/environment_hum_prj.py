#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
environment_hum_prj.py

This configuration file establishes the computational environment for the mineral earth hummock mapping project.
It imports required libraries, sets the project directory structure, initializes geospatial and plotting tools, and defines shared settings used by all downstream analysis scripts.
The file ensures reproducibility and consistent access to data, results, and processing resources across the workflow.

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-06
Version: 1.0
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
# Exactextract
import exactextract
# ---------------------------------------------------------------------------------------------------- #
# Numpy Typing
import numpy.typing as npt
# ---------------------------------------------------------------------------------------------------- #
# Matplotlib
from matplotlib.colors import LinearSegmentedColormap
# ---------------------------------------------------------------------------------------------------- #
# Rasterio
import rasterio.features
import rasterio.io
from rasterio.transform import from_bounds
# ---------------------------------------------------------------------------------------------------- #
# Rioxarray
import rioxarray
# ---------------------------------------------------------------------------------------------------- #
# Scipy
from scipy.spatial.distance import pdist
from scipy.stats import chi2_contingency
# ---------------------------------------------------------------------------------------------------- #
# Shapely
from shapely.geometry import shape
# ---------------------------------------------------------------------------------------------------- #
# Sklearn
from sklearn import set_config
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.utils.parallel import Parallel, delayed
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
