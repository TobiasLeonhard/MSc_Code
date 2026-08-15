#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
climate_normals.py

Description:
This utility module provides helper functions for processing climate data. 
It includes functions to flatten multi-level DataFrame column hierarchies, intelligently rename aggregated climate variables (temperature, precipitation) with statistical descriptors (mean, min, max, sum), and load gap-filled meteorological data from Trail Valley Creek. 
The functions support data aggregation workflows and column naming conventions used throughout the climate analysis pipeline.

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
from config.environment import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def flatten_columns(df: pd.DataFrame, column_fill: str) -> pd.DataFrame:
	"""
	Flattens multi-level column names in a DataFrame by joining the levels with a specified string.

	Args:
		df - pd.DataFrame: Input DataFrame with multi-level columns (e.g., from groupby aggregation).
		column_fill - str: String to insert between parts of the column name.

	Returns:
		flat_df = pd.DataFrame: DataFrame with flattened column names.
	"""
	flat_df = df.copy()
	flat_df.columns = ['Date'] + [f"{col[0]}_{column_fill}_{col[1]}" for col in flat_df.columns[1:]]
	return flat_df

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def rename_monthly_columns(col: str) -> str | None:
    """
    Rename columns according to the specified pattern

    Args:
        col - str: Col to rename

    Returns:
        ren_col - str: renamed col
    """
    # Handle Date column
    if col == "Date":
        return col

    # Extract the variable prefix
    parts = col.split("_")
    var = parts[0]

    # Pre-calculate counts to make logic cleaner
    mean_count = col.count("mean")
    sum_count = col.count("sum")
    min_count = col.count("min")
    max_count = col.count("max")

    # Pattern matching
    if mean_count == 2:
        return f"{var}_monthly_mean"
    elif sum_count == 2:
        return f"{var}_monthly_sum"
    elif min_count == 2:
        return f"{var}_monthly_extreme_min"
    elif max_count == 2:
        return f"{var}_monthly_extreme_max"
    elif min_count == 1 and mean_count == 1:
        return f"{var}_monthly_min"
    elif max_count == 1 and mean_count == 1:
        return f"{var}_monthly_max"

    # Otherwise: Return None
    return None
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_tvc_gap_filled_data() -> pd.DataFrame:
    """
    Checks whether data is available and if not raises error with information where to find it
    Args:

    Returns:
        climate_data - pd.DataFrame
    """

    # Load data
    data_path = data_folder / "tvc_data" / "meteorology" / Path("TVC_Gapfilled_Met_1991-2023").with_suffix(".xlsx")
    if data_path.exists():
        climate_data = pd.read_excel(data_path, sheet_name = "Gapfilled_Met")
    else:
        raise FileNotFoundError(f"The file {data_path.name} was not found, please download it from 'https://doi.org/10.5683/SP3/BXV4DE'.")

    return climate_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
