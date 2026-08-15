#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
gpr_processing_iwp_prj.py

Description:
This module integrates GPR, GNSS, and field measurements for ice-wedge polygon analysis.
It loads radargrams with reflection picks, adds active layer measurements, calculates velocity-corrected frost table depths and volumetric soil water content using dielectric properties, and classifies subsurface moisture conditions.
The module also aggregates multiple transect datasets into site-wide GeoDataFrames with consistent orientation and spatial reference, enabling comprehensive permafrost characterization.

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-14
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment_iwp_prj import *
from config.environment import *
from utility_functions.gnss_handling import load_gp2_data, fill_missing_traces, correct_gnss_with_rtk
from utility_functions.general import adjust_column_types
from utility_functions.combine_tifs import get_combined_raster
from utility_functions.active_layer_thickness import load_active_layer_data
from utility_functions.gpr_processing import crop_transect_data, combine_gpr_gnss_and_load_tif_file, add_pick_line, load_values_from_tif_file, add_active_layer_thickness_to_transect_data, calculate_frost_table_depths_and_bulk_volumetric_soil_water_content, calculate_ground_velocities, classify_by_thresholds, add_surface_topography_to_gpr_trace
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_data_for_iwp_transect(sgy_file: Path, pck_file: Path, tif_files: dict, used_velocities_m_ns: dict, classification_thresholds: dict, epsg_code: int = 3155, cut_half_width_m: float = 10.0, drop_frozen_table_measurements: Union[np.ndarray, None] = None, assumed_features: Union[dict, None] = None) -> Tuple[gpd.GeoDataFrame, dict]:
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
        used_on_iwp = True
        )

    # Add values from TIF (for example trough mapping)
    transect_data = load_values_from_tif_file(
        tif_file = tif_files["Trough Mapping"]["path"],
        gdf = transect_data,
        new_col_name = "iwp_mapping_values"
        )

    sampling_period = [pd.to_datetime("2025-07-20 00:00:00", utc = True), pd.to_datetime("2025-07-27 00:00:00", utc = True)]
    transect_data = add_active_layer_thickness_to_transect_data(
        sgy_stem = sgy_file.stem,
        transect_data = transect_data,
        used_velocities_m_ns = used_velocities_m_ns,
        rotational_info = image_data["rotational_info"],
        sampling_period = sampling_period,
        drop_frozen_table_measurements = drop_frozen_table_measurements,
        epsg_code = epsg_code
        )

    transect_data = calculate_ground_velocities(
        gdf = transect_data,
        feature_correction = assumed_features,
        used_velocities = used_velocities_m_ns
        )

    transect_data = calculate_frost_table_depths_and_bulk_volumetric_soil_water_content(
        gdf = transect_data
        )

    # Add "volumetric_soil_moisture_classification" column to the transect data
    transect_data = classify_by_thresholds(
        gdf = transect_data,
        classification_thresholds = classification_thresholds
        )

    transect_data = add_surface_topography_to_gpr_trace(
        gdf = transect_data
        )

    return transect_data, image_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_iwp_gdfs(path_to_gdfs: Path)  -> gpd.GeoDataFrame:
    """
    Loads IWP GeoDataFrames from a given path using parquet and concatenates them if multiple files are found.

    Args:
        path_to_gdfs - Path: The file path to load the GeoDataFrames from.

    Returns:
        gdf - gpd.GeoDataFrame: The loaded GeoDataFrames.
    """
    gdf = None
    gdfs_list = []

    for file in path_to_gdfs.iterdir():
        if "IWP" not in file.stem or file.suffix != ".parquet":
            continue
        if "subtransect" in file.stem:
            continue

        print("Loading file:", file.stem)
        temp_gdf = gpd.read_parquet(file)

        # Handle orientation logic
        if "E-S" in file.stem:
            # Reverse and reset index
            temp_gdf = temp_gdf.iloc[::-1].reset_index(drop=True)
            temp_gdf["distance_from_starting_pos_m"] = temp_gdf["distance_from_starting_pos_m"].max() - temp_gdf["distance_from_starting_pos_m"]
        elif "S-E" in file.stem:
            # Keep as is
            pass
        temp_gdf["study_site_id"] = file.stem.split("_")[2]  # Extract study site ID from filename
        gdfs_list.append(temp_gdf)

    # Combine everything at once
    if gdfs_list:
        # Use GeoPandas specific concat logic or wrap pd.concat
        gdf = gpd.GeoDataFrame(pd.concat(gdfs_list, ignore_index=True), crs=gdfs_list[0].crs)
    else:
        raise ValueError(f"Did not find any matching files in {path_to_gdfs}.")

    return gdf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
