#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
general.py

This file contains functions used from different functions.

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
from config.environment import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def parse_hhmmss(time_str:str) -> str:
    """
    Convert HHMMSS.SS format to HH:MM:SS format

    Args:
        time_str: time in HHMMSS.SS format

    Returns:
        time: time in HH:MM:SS format
    """
    time_float = float(time_str)
    hours = int(time_float // 10000)
    minutes = int((time_float % 10000) // 100)
    seconds = time_float % 100
    time = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    return time

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def adjust_column_types(df: Union[pd.DataFrame, gpd.GeoDataFrame], column_types: dict) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
    """
    Adjusts the data types of specified columns in a DataFrame.

    Args:
        df - pd.DataFrame or gpd.GeoDataFrame: The input DataFrame.
        column_types - dict: A dictionary mapping column names to desired data types.

    Returns:
        df - pd.DataFrame or gpd.GeoDataFrame: The DataFrame with adjusted column types.
    """
    if isinstance(df, gpd.GeoDataFrame):
        is_gdf = True
        gdf_crs = df.crs
    else:
        is_gdf = False
    for column, dtype in column_types.items():
        if column in df.columns:
            if dtype == "geometry":
                if isinstance(df[column].iloc[0], str) and is_gdf == True:
                    df[column] = gpd.GeoSeries.from_wkt(df[column])
                else:
                    df[column] = df[column].astype(dtype)
            else:
                df[column] = df[column].astype(dtype)

    existing_keys = [k for k in column_types.keys() if k in df.columns]
    df = df.loc[:, existing_keys]
    if "geometry" in df.columns and is_gdf == True:
        df = gpd.GeoDataFrame(df, geometry = "geometry", crs = gdf_crs)
    return df

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def dmm_to_decimal(val: float) -> float:
    """
    Converts a dmm coordinate to a decimal coordinate

    Args:
        val - float: Dmm value

    Return:
        dec - float: Value in decimal
    """
    if abs(val) >= 10000:
        degrees = int(val // 100)      # 3-digit degrees expected
    else:
        degrees = int(val // 100)      # 2-digit degrees for lat
    minutes = val - degrees*100
    dec = degrees + minutes/60.0
    return dec

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def calculate_distance_from_start(data: gpd.GeoDataFrame, control_points: gpd.GeoDataFrame, distance_col: str) -> gpd.GeoDataFrame:
    """
    Calculates the distance of points to start points and returns a GeoDataFrame with an additional column containing it

    Args:
        data - gpd.GeoDataFrame: Original data frame where distance is added
        control_points - gpd.GeoDataFrame: Data frame with control points used to calculate the distance
        distance_col - str: Name of the col that is used for calculating distance from start

    Returns:
        data_with_distance_to_start - gpd.GeoDataFrame: Data frame containing the distances in the "Distance-to-Start-of-Transect (m)" column
    """
    data_with_distance_to_start = data.copy()

    data_with_distance_to_start[distance_col] = np.nan
    # Group the DataFrame by study_site_id
    grouped = data_with_distance_to_start.groupby("study_site_id")
    for site_id_raw, group in grouped:
        site_id = str(site_id_raw)
        if site_id == "Lysometer-Patch":
            continue
        elif "IWP" in site_id:
            start_point = site_id[:-2]
        elif "Siksik" in site_id:
            start_point = site_id + "-Start"
        else:
            raise ValueError("This site id is not implemented.")
        start_geom = control_points.loc[control_points["study_site_id"] == start_point, "geometry"]
        if start_geom.empty:
            raise ValueError("Controil point has no geometry, cannot calculate distance.")
        else:
             group[distance_col] = group.geometry.distance(start_geom.iloc[0])
        data_with_distance_to_start.loc[group.index, distance_col] = group[distance_col]
    return data_with_distance_to_start

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
