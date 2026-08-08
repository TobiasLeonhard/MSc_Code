#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
environment.py

This environment file imports and organizes all packages.
Additionally, it defines paths for the project.

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
# Calendar
import calendar
# ---------------------------------------------------------------------------------------------------- #
# Contextlib
from contextlib import ExitStack #
# ---------------------------------------------------------------------------------------------------- #
# Gc
import gc
# ---------------------------------------------------------------------------------------------------- #
# Os
import os
# ---------------------------------------------------------------------------------------------------- #
# Re
import re
# ---------------------------------------------------------------------------------------------------- #
# Subprocess
import subprocess
# ---------------------------------------------------------------------------------------------------- #
# Sys
import sys
# ---------------------------------------------------------------------------------------------------- #
# Typing
from typing import Union, Tuple, List, Dict, Any, cast
# ---------------------------------------------------------------------------------------------------- #
# Pathlib
from pathlib import Path
# ---------------------------------------------------------------------------------------------------- #
# Warnings
import warnings
# ---------------------------------------------------------------------------------------------------- #
# XML ET
import xml.etree.ElementTree as ET
# ---------------------------------------------------------------------------------------------------- #

# ==================================================================================================== #
# Third-Party Libraries
# ---------------------------------------------------------------------------------------------------- #
# Exactextract
import exactextract
# ---------------------------------------------------------------------------------------------------- #
# Fiona
import fiona
# ---------------------------------------------------------------------------------------------------- #
# Geocube
from geocube.api.core import make_geocube
# ---------------------------------------------------------------------------------------------------- #
# Geopandas
import geopandas as gpd
# ---------------------------------------------------------------------------------------------------- #
# Geopy
from geopy.distance import geodesic
# ---------------------------------------------------------------------------------------------------- #
# Matplotlib
import matplotlib as mpl
import matplotlib.axes
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize, ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
# ---------------------------------------------------------------------------------------------------- #
# Numpy
import numpy as np
import numpy.typing as npt
# ---------------------------------------------------------------------------------------------------- #
# Pandas
import pandas as pd
# ---------------------------------------------------------------------------------------------------- #
# Pyproj
from pyproj import CRS, Transformer
# ---------------------------------------------------------------------------------------------------- #
# Rasterio
import rasterio
import rasterio.crs
import rasterio.enums
import rasterio.features
import rasterio.io
import rasterio.transform
import rasterio.warp
import rasterio.windows
from rasterio import features
from rasterio.enums import ColorInterp
from rasterio.errors import NodataShadowWarning
from rasterio.features import shapes
from rasterio.mask import mask
from rasterio.transform import from_bounds
from rasterio.vrt import WarpedVRT
from rasterio.warp import reproject, Resampling
from rasterio.windows import Window
# ---------------------------------------------------------------------------------------------------- #
# Rioxarray
import rioxarray
# ---------------------------------------------------------------------------------------------------- #
# Scipy
import scipy
from scipy.constants import speed_of_light
from scipy.ndimage import rotate as ndimage_rotate
from scipy.signal import savgol_filter
from scipy.spatial.distance import pdist, squareform, cdist
from scipy.stats import chi2_contingency
# ---------------------------------------------------------------------------------------------------- #
# segyio
import segyio
# ---------------------------------------------------------------------------------------------------- #
# Shapely
from shapely.geometry import shape, Point, LineString
# ---------------------------------------------------------------------------------------------------- #
# Sklearn
from sklearn import set_config
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import cohen_kappa_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.utils.parallel import Parallel, delayed
# ---------------------------------------------------------------------------------------------------- #
# Whitebox
import whitebox
# ---------------------------------------------------------------------------------------------------- #
# Xarray
import xarray as xr
# ---------------------------------------------------------------------------------------------------- #
# ==================================================================================================== #

# ==================================================================================================== #
# Defining Paths and more
# ---------------------------------------------------------------------------------------------------- #
if "project_path" not in globals():
    # Initiate whitebox
    wbt = whitebox.WhiteboxTools()

    # Define Paths
    project_path = Path(__file__).resolve().parent.parent
    coding_folder = Path(__file__).resolve().parent.parent
    data_folder = coding_folder / "data"
    results_folder = coding_folder / "results"
    dtm_calculations_folder =  results_folder / "dtm_calculations"
    manual_input_folder = coding_folder / "manual_input_data"
    if not manual_input_folder.exists():
        raise FileNotFoundError("Manual input data not found.")
    if not data_folder.exists():
        raise FileNotFoundError("Data not found.")

    # Create Folders
    data_folder.mkdir(exist_ok = True)
    results_folder.mkdir(exist_ok = True)
    dtm_calculations_folder.mkdir(exist_ok = True)

    # Filter warnings
    os.environ["PYTHONWARNINGS"] = "ignore::UserWarning:sklearn.utils.parallel"
    warnings.filterwarnings("ignore", category = RuntimeWarning, message = ".*'Memory' driver is deprecated.*")
    warnings.filterwarnings("ignore", category = NodataShadowWarning)

    # Set plotting settings
    DPI = 300
    legend_fontsize = 14
    matplotlib_settings = {
        "font.family": "Times New Roman",  # Set font to Times New Roman
        "font.size": 16,                  # Default font size
        "axes.titlesize": 20,             # Title size
        "axes.labelsize": 16,             # Axis label size
        "legend.fontsize": legend_fontsize             # Legend size
        }
    custom_colors = {
        "wlu_purple": "#924da7"
        }
    plt.rcParams.update(cast(Any, matplotlib_settings))

project_path_str = str(project_path)
if project_path_str not in sys.path:
    sys.path.append(project_path_str)
# ==================================================================================================== #
