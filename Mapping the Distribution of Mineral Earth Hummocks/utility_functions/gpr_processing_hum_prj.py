#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
gpr_processing.py

This file contains functions for processing GPR related data

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-06
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
from utility_functions.gpr_processing import combine_gpr_gnss_and_load_tif_file, add_pick_line, load_values_from_tif_file
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_data_for_hummock_detection(sgy_file: Path, pck_file: Path, tif_files: dict, epsg_code: int = 3155, cut_half_width_m: float = 10.0) -> Tuple[gpd.GeoDataFrame, dict]:
    """
    Loads the data needed for plotting for the IWP analysis.

    Args:
        sgy_file - Path: Path to the SGY file.
        pck_file - Path: Path to the PCK file.
        tif_files - dict: List of dictionaries containing TIFF file paths and resampling methods and wanted bands
        used_velocities_m_ns - dict: Dictionary of used velocities.
        classification_thresholds - dict: Dictonary for soil classifications.
        epsg_code - int: Code of the EPSG unit. Defaults to 3155
        cut_half_width_m float: Half-width in meters for cropping the orthomosaic around the transect. Defaults to 10.0
        drop_frozen_table_measurements - np.ndarray: Array of frost table measurements to drop. Defaults to None
        assumed_features - dict: A dictionary of assumed ground features. Defaults to None

    Returns:
        transect_data - gpd.GeoDataFrame: A GeoDataFrame containing all needed transect data information for plotting and processing
        image_data - dict: A dictionary containing information for plotting.
    """
    # Get GPR and GNSS
    transect_data, image_data = combine_gpr_gnss_and_load_tif_file(
        sgy_file = sgy_file,
        tif_files = tif_files,
        cut_half_width_m = cut_half_width_m
        )

    # Add pick line
    transect_data = add_pick_line(
        gdf = transect_data,
        pck_file = pck_file,
        used_on_iwp = False
        )

    # Add values from TIF (for example Hummock Mapping)
    transect_data = load_values_from_tif_file(
        tif_file = tif_files["Hummock Mapping"]["path"],
        gdf = transect_data,
        new_col_name = "hummock_mapping_values"
        )
    compare_hummock_identification_methods(
        gdf = transect_data
        )
    return transect_data, image_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def compare_hummock_identification_methods(gdf: gpd.GeoDataFrame) -> None:
    """
    Compares the mapping results between mapped and identified hummocks.

    Args:
        gdf - gpd.GeoDataFrame: Data frame containing the transect data
    """
        # 1. Basic Counts
    tp = len(gdf[(gdf["is_hummock"] == True) & (gdf["hummock_mapping_values"] == 1)])
    fp = len(gdf[(gdf["is_hummock"] == False) & (gdf["hummock_mapping_values"] == 1)])
    fn = len(gdf[(gdf["is_hummock"] == True) & (gdf["hummock_mapping_values"] != 1)])

    gpr_total = len(gdf[gdf["is_hummock"] == True])
    tif_total = len(gdf[gdf["hummock_mapping_values"] == 1])

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    bias = (tif_total - gpr_total) / gpr_total if gpr_total > 0 else 0
    kappa = cohen_kappa_score(gdf["is_hummock"], gdf["hummock_mapping_values"])

    print(f"--- Comparison Results ---")
    print(f"Precision: {precision:.2%} (How many of the mapped hummocks are correctly identified in the GPR-based identification)")
    print(f"Recall: {recall:.2%} (How many of the mapped hummocks are not found in the GPR-based identification)")
    print(f"F1 Score: {f1score:.2%} (Harmonic mean of precision and recall)")
    print(f"Bias: {bias:.2%} (Relative difference in total counts between GPR-based and TIF-based identification)")
    print(f"Cohen's Kappa: {kappa:.2f} (Agreement between GPR-based and TIF-based identification)")
    print(f"--------------------------")
    print(f"GPR Total Hummock Points: {gpr_total}")
    print(f"TIF Total Hummock Points: {tif_total}")
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------")

    return None

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
