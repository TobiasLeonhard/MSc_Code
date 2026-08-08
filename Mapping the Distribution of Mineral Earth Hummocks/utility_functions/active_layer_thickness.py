#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
active_layer_thickness.py

This file contains functions for handling the frost table/active layer thickness data

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
from utility_functions.gnss_handling import load_klm_data
from utility_functions.general import adjust_column_types, calculate_distance_from_start
from utility_functions.gnss_handling import load_control_points
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def pre_clean_active_layer_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-cleans and reshapes the active layer depth data.

    Args:
        df - pd.DataFrame: Raw active layer depth data in wide format.

    Returns:
        pre_cleaned_df - pd.DataFrame: Cleaned and reshaped data in long format.
    """
	# Initialize an empty DataFrame for the reshaped data
    pre_cleaned_df = pd.DataFrame(
        columns = [
            "Date",
            "Study-Site-ID",
            "Measurement-Number",
            "Negative-Active-Layer",
            "Active-Layer-Probe-Length",
            "Comment"
	        ]
        )

	# Extract study site IDs from column names
    study_site_ids = [col[5:] for col in df.columns if col.startswith("Date-")]

	# Group columns by study site ID
    columns_by_site = {
		site_id: [col for col in df.columns if site_id in col]
		for site_id in study_site_ids
	}
    column_names = [
		"Date",
		"Study-Site-ID",
		"Measurement-Number",
		"Negative-Active-Layer",
		"Active-Layer-Probe-Length",
		"Comment"
	]
    pre_cleaned_df = pd.DataFrame({col: pd.Series(dtype="object") for col in column_names})
	# Process each study site ID and reshape its data
    for site_id, columns in columns_by_site.items():
        # Extract relevant columns for the current study site
        date_col = df.get(f"Date-{site_id}", pd.Series(dtype = "object")).dropna()
        meas_num_col = df.get(f"Measurement-Number-{site_id}",  pd.Series(dtype = "object")).dropna()
        depth_col = df.get(f"Negative-Active-Layer-{site_id}",  pd.Series(dtype = "object")).dropna()
        probe_len_col = df.get(f"Active-Layer-Probe-Length-{site_id}",  pd.Series(dtype = "object")).dropna()
        comment_col = df.get(f"Comment-{site_id}",  pd.Series(dtype = "object")).dropna()
        # Ensure all columns have the same length before appending
        if len(date_col) == len(meas_num_col) == len(depth_col) == len(probe_len_col) == len(comment_col):
            temp_df = pd.DataFrame({
                "Date": date_col,
                "Study-Site-ID": [site_id] * len(date_col),
                "Measurement-Number": meas_num_col,
                "Negative-Active-Layer": depth_col,
                "Active-Layer-Probe-Length": probe_len_col,
                "Comment": comment_col
            })
            # Check for NA values and print a warning if any are found
            if temp_df.isna().any().any():
                print(f"Warning: NA values found for Study Site ID: {site_id}")
            # Drop NA values and concatenate
            if not pre_cleaned_df.empty:
                pre_cleaned_df = pd.concat([pre_cleaned_df, temp_df], ignore_index=True)
            else:
                pre_cleaned_df = temp_df

        else:
            # Log a warning if column lengths mismatch
            print(f"Column length mismatch for Study Site ID: {site_id}")
    pre_cleaned_df.rename(
        columns = {
            "Date": "datetime_utc",
            "Study-Site-ID": "study_site_id",
            "Measurement-Number": "measurement_number",
            "Negative-Active-Layer": "negative_active_layer_length_cm",
            "Active-Layer-Probe-Length": "active_layer_probe_length_cm",
            "Comment": "comment"
            },
        inplace=True
        )
    return pre_cleaned_df

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def import_rtk_data(gnss_folder: Path) -> gpd.GeoDataFrame:
	"""
	Imports RTK data from KML files and processes it into a structured DataFrame.

	Parameters:
	    gnss_folder - Path: Path to the folder containing KML files.

	Returns:
	    gdf - gpd.GeoDataFrame: Processed RTK data with columns for coordinates, date, study site ID, and measurement number.
	"""
	# Convert to DataFrame for easier handling
	gdf = load_klm_data(gnss_folder)

	# Process the "name" column to extract date, study site ID, and measurement number
	gdf["datetime_utc"] = pd.to_datetime(gdf["name"].str[:10], format = "%Y-%m-%d", errors = "coerce")
	gdf["study_site_id"] = gdf["name"].str[11:-3]
	gdf["measurement_number"] = pd.to_numeric(gdf["name"].str[-2:], errors = "coerce")
	# Replace empty entries in "study_site_id" with "Lysometer-Patch"
	gdf["study_site_id"] = gdf["study_site_id"].replace("", "Lysometer-Patch")
	# Drop the "name" column as it is no longer needed
	gdf.drop(columns = ["name"], inplace = True)
	gdf["study_site_id"] = gdf["study_site_id"].replace(
        {
            "L1": "Siksik-Lower-1",
            "L2": "Siksik-Lower-2",
            "L3": "Siksik-Lower-3",
            "U1": "Siksik-Upper-1",
            "U2": "Siksik-Upper-2",
            "U3": "Siksik-Upper-3",
            "U4": "Siksik-Upper-4",
            "U5": "Siksik-Upper-5",
            "U6": "Siksik-Upper-6",
            "M1": "Siksik-Middle-1",
            "M2": "Siksik-Middle-2",
            "M3": "Siksik-Middle-3",
            "M4": "Siksik-Middle-4",
            "M5": "Siksik-Middle-5",
            # Correcting mislabeled entries
            "L6": "Siksik-Middle-6",
            "M6": "Siksik-Middle-6",
            # Correcting mislabeled entries
            "L7": "Siksik-Middle-7",
            "M7": "Siksik-Middle-7",
            # Correcting mislabeled entries
            "L8": "Siksik-Middle-8",
            "M8": "Siksik-Middle-8",
            # Correcting mislabeled entries
            "L9": "Siksik-Middle-9",
            "M9": "Siksik-Middle-9",
            }
        )

	return gdf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def merge_rtk_and_active_layer_data(alt_df: pd.DataFrame, rtk_df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Merges active layer depth data with RTK data on common columns and creates a GeoDataFrame.

    Parameters:
        alt_df - pd.DataFrame: Active layer depth data.
        rtk_df - gpd.GeoDataFrame: Rtk data.
    Returns:
        alt_gdf - gpd.GeoDataFrame: Merged DataFrame containing both active layer depth and GPS information.
    """
    # Find extra rows - That are not covered in the other data frame
    extra_rows_in_rtk_data = rtk_df.merge(
        alt_df,
        how = "left",
        on = ["datetime_utc", "study_site_id", "measurement_number"],
        indicator = True
        ).query("_merge == 'left_only'")

    extra_rows_in_alt_data = alt_df.merge(
        rtk_df,
        how = "left",
        on = ["datetime_utc", "study_site_id", "measurement_number"],
        indicator = True
        ).query("_merge == 'left_only'")

    # Check whether anything was found and drop them
    if not extra_rows_in_rtk_data.empty:
        print(f"Warning: There are {len(extra_rows_in_rtk_data)} extra rows in the RTK data that do not have matching entries in the active layer data, these data entries will be dropped.")
        rtk_df = rtk_df[~rtk_df.index.isin(extra_rows_in_rtk_data.index)]

    if not extra_rows_in_alt_data.empty:
        print(f"Warning: There are {len(extra_rows_in_alt_data)} extra rows in the active layer data that do not have matching entries in the RTK data, these data entries will be dropped.")
        alt_df = alt_df[~alt_df.index.isin(extra_rows_in_alt_data.index)]

	# Merge the cleaned active layer depth data with the GPS data
    alt_gdf = rtk_df.merge(
            alt_df,
            on = ["datetime_utc", "study_site_id", "measurement_number"],
            how = "inner"
        )
    alt_gdf["datetime_utc"] = pd.to_datetime(alt_gdf["datetime_utc"], utc = True)
    return alt_gdf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def assign_topographic_features(active_layer_data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Assigns topographic features based on comments in the active layer data.

    Parameters:
        active_layer_data - gpd.GeoDataFrame: DataFrame containing active layer data with a 'comment' column.

    Returns:
        active_layer_data - gpd.GeoDataFrame: Updated DataFrame with a new column 'Assigned Topographic Feature'.
    """
    # Group data based on the presence of 'IH' or 'H' in the comments
    conditions = [
        active_layer_data["comment"].str.contains("IH", na = False) & ~active_layer_data["comment"].str.contains("C/H2O", na = False),
        active_layer_data["comment"].str.contains("H", na = False) & ~active_layer_data["comment"].str.contains("C/H2O", na = False),
        active_layer_data["comment"].str.contains("C/H2O", na = False)
    ]

    # Define the choices corresponding to the conditions.
    choices = ["IH", "H", "C/H2O"]

    # Assign choices, if not clear assing NaT
    active_layer_data["assigned_topographic_feature"] = np.select(
        conditions,
        choices,
        default = "NaT"
        )
    active_layer_data.loc[active_layer_data["study_site_id"].str.contains("IWP", na = False), "assigned_topographic_feature"] = "NaT"
    return active_layer_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def generate_active_layer_data() -> gpd.GeoDataFrame:
    """
    Generates the active layer data file.

    Args:
        output_file - Path: Path where the file is stored

    Returns:
        active_layer_data - gpd.GeoDataFrame: GeoDataFrame containing GNSS locations and active layer data
    """
    # Define the input file of the raw data and load it
    field_data_folder = data_folder / "field_data_2025"
    active_layer_data_raw_file = field_data_folder / Path("2025-06-30 - Active Layer Depth").with_suffix(".xlsx")
    active_layer_data_raw = pd.read_excel(
        active_layer_data_raw_file,
        sheet_name = "Active_Layer_Depth",
        header = 3
        )
    active_layer_data_pre_clean = pre_clean_active_layer_data(active_layer_data_raw)
    # Load RTK data from KML files and add them to the active layer data
    rtk_folder = field_data_folder / "2025-06-30 - Active Layer Depth - RTK"
    rtk_data = import_rtk_data(rtk_folder)
    active_layer_data_pre_clean_and_rtk = merge_rtk_and_active_layer_data(
        alt_df = active_layer_data_pre_clean,
        rtk_df = rtk_data
        )
    # calculate distance from start
    control_points = load_control_points()
    active_layer_data = calculate_distance_from_start(
        data = active_layer_data_pre_clean_and_rtk,
        control_points = control_points,
        distance_col = "distance_from_start_of_transect_m"
        )
    active_layer_data["active_layer_thickness_m"] = (pd.to_numeric(active_layer_data["active_layer_probe_length_cm"]) - pd.to_numeric(active_layer_data["negative_active_layer_length_cm"])) / 100.0
    active_layer_data = assign_topographic_features(
        active_layer_data = active_layer_data
        )

    column_types = {
        "datetime_utc": "datetime64[ns, UTC]",
        "study_site_id": "string",
        "measurement_number": "int64",
        "negative_active_layer_length_cm": "float64",
        "active_layer_probe_length_cm": "float64",
        "active_layer_thickness_m": "float64",
        "comment": "string",
        "distance_from_start_of_transect_m": "float64",
        "elevation": "float64",
        "assigned_topographic_feature": "string",
        "geometry": "geometry"
    }
    active_layer_data = adjust_column_types(
        df = active_layer_data,
        column_types= column_types
        )
    # Ensure that it is an gdf
    assert isinstance(active_layer_data, gpd.GeoDataFrame)
    return active_layer_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_active_layer_data() -> gpd.GeoDataFrame:
    """
    Loads the active layer data from 2025.
    If the file is not found it is generated.
    Return is a gpd.GeoDataFrame

    Returns:
        active_layer_data - gpd.GeoDataFrame: GeoDataFrame containing the active layer data and the GNSS data.
    """
    # Define file
    active_layer_data_file = results_folder / "cleaned_data" / Path("cleaned_active_layer_data").with_suffix(".parquet")

    # Load or generate it
    if active_layer_data_file.exists():
        active_layer_data = gpd.read_parquet(active_layer_data_file)
    else:
        active_layer_data = generate_active_layer_data()
        active_layer_data.to_parquet(active_layer_data_file)

    if not active_layer_data_file.with_suffix(".gpkg").exists():
        gpkg_active_layer_data = active_layer_data.rename(
            columns = {
                "study_site_id": "site_id",
                }
            )
        gpkg_active_layer_data.to_file(active_layer_data_file.with_suffix(".gpkg"), driver = "GPKG")
    return active_layer_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
