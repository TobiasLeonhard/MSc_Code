#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
gnss_handling.py

This file contains functions for handling gnss data

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
from utility_functions.general import parse_hhmmss, dmm_to_decimal, adjust_column_types
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_control_points() -> gpd.GeoDataFrame:
    """
        Generates or loads RTK controll points.

        Returns:
            control_points - gpd.GeoDataFrame: Data Frame with controll points
    """
    path_to_controll_points = data_folder / "field_data_2025" / "2025-09-24 - Controll Points"

    output_file = results_folder / "cleaned_data" / Path("control_points").with_suffix(".parquet")
    output_file.parent.mkdir(exist_ok = True)
    if output_file.exists():
        control_points = gpd.read_parquet(output_file)
    else:
        control_points = load_klm_data(path_to_controll_points)
        control_points["name"] = control_points["name"].str.replace(r"IWP-GPR-0*(\d+)", r"IWP-\1", regex = True)
        pattern = r"(Upper|Middle|Lower)\s+(\d+)\s+(End|Start)"
        replacement = r"Siksik-\1-\2-\3"
        control_points["name"] = control_points["name"].str.replace(pattern, replacement, regex = True)
        control_points = control_points.rename(columns={
                "name": "study_site_id",
                }
            )
        control_points_columns = {
            "study_site_id": "string",
            "elevation_m": "float64",
            "longitude": "float64",
            "latitude": "float64",
            "geometry": "geometry"
            }
        control_points = cast(gpd.GeoDataFrame, adjust_column_types(control_points, control_points_columns))
        control_points.to_parquet(output_file.with_suffix(".parquet"))
    if not output_file.with_suffix(".gpkg").exists():
        gpkg_control_points = control_points.rename(columns={
            "study_site_id": "site_id",
            }
        )
        gpkg_control_points.to_file(output_file.with_suffix(".gpkg"), driver = "GPKG")

    return control_points

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_klm_data(gnss_path: Path) -> gpd.GeoDataFrame:
    """
    Loads gnss data from a specified path.

    Args:
        gnss_path - Path: Path to the GNSS data file or folder

    Returns:
        gnss_points - gpd.GeoDataFrame: Loaded GNSS data.
    """
    # Check whether it is a file or a folder
    if gnss_path.suffix == ".klm":
        kml_files = [gnss_path]
    else:
        kml_files = list(Path(gnss_path).glob("*.kml"))

    gnss_points = []
    # Namespace for parsing KML files
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    print(f"Loading GPS data from {len(kml_files)} KML files.")
    for kml_file in kml_files:
        with open(kml_file, "rt", encoding = "utf-8") as f:
            doc = f.read()
        root = ET.fromstring(doc)

        for placemark in root.findall(".//kml:Placemark", ns):
            point_data = {}
            # Get Placemark name
            name_elem = placemark.find("kml:name", ns)
            if name_elem is not None:
                point_data["name"] = name_elem.text
            # Get all SimpleData fields
            for sd in placemark.findall(".//kml:SimpleData", ns):
                key = sd.attrib.get("name")
                value = sd.text
                point_data[key] = value
            # Get coordinates
            coord_elem = placemark.find(".//kml:coordinates", ns)
            if coord_elem is not None and coord_elem.text is not None:
                coords = coord_elem.text.strip().split(",")

                if len(coords) >= 2:
                    point_data["Longitude_coord"] = coords[0]
                    point_data["Latitude_coord"] = coords[1]
                    if len(coords) > 2:
                        point_data["Ellipsoidal_height_coord"] = np.float64(coords[2])
            gnss_points.append(point_data)
    gnss_points = pd.DataFrame(gnss_points)
    cs_name = gnss_points["CS name"]
    if len(cs_name.unique()) == 1:
        if cs_name.unique()[0] == "NAD83(CSRS) / UTM zone 8N + CGVD28 height":
            gnss_gdf = gpd.GeoDataFrame(
                gnss_points,
                geometry = gpd.points_from_xy(gnss_points["Easting"], gnss_points["Northing"]),
                crs = "EPSG:3155"
                )
            columns_to_drop = [
                "Easting", "Northing", "Longitude", "Latitude", "Ellipsoidal height", "Origin", "Easting RMS", "Northing RMS",
                "Elevation RMS", "Lateral RMS", "Antenna height", "Antenna height units", "Solution status", "Correction type",
                "Averaging start", "Averaging end", "Samples", "GDOP", "Base easting", "Base northing",  "Base elevation",
                "Base longitude", "Base latitude", "Base ellipsoidal height", "Baseline", "CS name", "GPS Satellites",
                "GLONASS Satellites", "Galileo Satellites", "BeiDou Satellites", "QZSS Satellites",
                "Ellipsoidal_height_coord", "Code", "Code description"
                ]

            gnss_gdf.drop(
                columns = columns_to_drop,
                inplace = True,
                errors = "ignore"
                )
            if "Elevation" in gnss_gdf.columns:
                gnss_gdf = gnss_gdf.rename(columns={
                        "Elevation": "elevation_m",
                        }
                    )
            if "Longitude_coord" in gnss_gdf.columns:
                gnss_gdf = gnss_gdf.rename(columns={
                        "Longitude_coord": "longitude",
                        }
                    )
            if "Latitude_coord" in gnss_gdf.columns:
                gnss_gdf = gnss_gdf.rename(columns={
                        "Latitude_coord": "latitude",
                        }
                    )
        else:
            raise ValueError(f"The provided CS ({cs_name.unique()[0].values}) is not implemented.")
    gnss_gdf_columns = {
        "name": "str",
        "elevation_m": "float64",
        "longitude": "float64",
        "latitude": "float64",
        "geometry": "geometry"
        }
    gnss_gdf = cast(gpd.GeoDataFrame, adjust_column_types(gnss_gdf, gnss_gdf_columns))
    return gnss_gdf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_gp2_data(gp2_path: Path, epsg_code: int = 3155) -> gpd.GeoDataFrame:
    """
    Load data from gp2 file and return it as a gpd.GeoDataFrame.

    Args:
        gp2_path - Path: File path to gp2 file
        epsg_code - int: EPSG code defaults to 3155

    Returns:
        gp2_data - gpd.GeoDataFrame: GP2 data in a GeoDataFrame
    """
    if not gp2_path.exists():
        raise FileNotFoundError(f"File {gp2_path} not found.")

    try:
        gp2_raw = pd.read_csv(
            gp2_path,
            header = 5,
            dtype = str,
            on_bad_lines = "warn",
            engine = "python"
            )
    except pd.errors.ParserError as e:
        print(f"ParserError encountered: {e}")
        print("Attempting to read with QUOTE_NONE...")
        gp2_raw = pd.read_csv(
            gp2_path,
            header = 5,
            dtype = str,
            quoting = 3,
            engine = "python"
            )

    date = str(
        pd.read_csv(
            gp2_path,
            nrows = 1,
            header = 2,
            dtype = {0: str}).iloc[0, 0]
        )[6:-9]
    if "Jul" in date:
        date = date.replace("Jul", "07")
    elif "May" in date:
        date = date.replace("May", "05")
    else:
        raise ValueError(f"Month setting unknown in date: {date}")

    # Extract data from the GPS column and select needed information
    gp2_gps = pd.DataFrame()
    gp2_gps[
        [
            "log_header",
            "time_utc",
            "latitude_ddmm.mm",
            "latitude_direction",
            "longitude_ddmm.mm",
            "longitude_direction",
            "quality",
            "number_of_satellites",
            "horizontal_dilution_of_precision",
            "antenna_altitude_above_ground",
            "units_of_antenna_altitude",
            "undulation",
            "units_of_undulation",
            "unknown_column",
            "check_sum"
            ]
        ] = gp2_raw["GPS"].str.split(",", expand = True)
    antenna_units = gp2_gps["units_of_antenna_altitude"].unique()
    gp2_gps = gp2_gps[["time_utc", "latitude_ddmm.mm", "latitude_direction", "longitude_ddmm.mm", "longitude_direction", "antenna_altitude_above_ground"]]
    gp2_raw = gp2_raw.drop(columns=["GPS"])
    gp2_raw.rename(columns={"time_elapsed(s)": "time_elapsed_s"}, inplace=True)
    gp2_df = gp2_raw.join(gp2_gps)

    # Convert HHMMSS.SS format to datetime
    gp2_df["time_formatted"] = gp2_df["time_utc"].astype(float).apply(parse_hhmmss)
    gp2_df["datetime_utc"] = pd.to_datetime(date + " " + gp2_df["time_formatted"], format = "%Y-%m-%d %H:%M:%S.%f", utc = True)
    gp2_df = gp2_df.drop(columns=["time_formatted", "time_utc"])

    # Convert ddmm to decimal
    gp2_df["longitude_dec"] = gp2_df["longitude_ddmm.mm"].astype(float).apply(dmm_to_decimal)
    gp2_df["latitude_dec"] = gp2_df["latitude_ddmm.mm"].astype(float).apply(dmm_to_decimal)
    gp2_df["longitude_dec"] = gp2_df.apply(lambda row: -row["longitude_dec"] if row["longitude_direction"] in ["W", "w"] else row["longitude_dec"], axis=1)
    gp2_df["latitude_dec"] = gp2_df.apply(lambda row: -row["latitude_dec"] if row["latitude_direction"] in ["S", "s"] else row["latitude_dec"], axis=1)

    if len(antenna_units) == 1 and antenna_units[0] == "M":
        gp2_df.rename(columns={"antenna_altitude_above_ground": "antenna_altitude_above_ground_m"}, inplace=True)
    else:
        raise ValueError("This elevation unit is not implemented.")

    # Select needed columns and remove dublicates
    gp2_df = gp2_df.rename(columns={
                "traces": "trace",
                }
            )
    gp2_df_columns = {
        "trace": "int64",
        "time_elapsed_s": "float64",
        "antenna_altitude_above_ground_m": "float64",
        "datetime_utc": "datetime64[ns, UTC]",
        "longitude_dec": "float64",
        "latitude_dec": "float64"
        }
    gp2_df = adjust_column_types(gp2_df, gp2_df_columns)
    gp2_df = gp2_df.groupby("trace").agg({
            "time_elapsed_s": "first",
            "longitude_dec": "mean",
            "latitude_dec": "mean",
            "antenna_altitude_above_ground_m": "mean",
            "datetime_utc": "first",
            }).reset_index()

    # Put it into a gdf and use the wanted epsg_code
    geometry = [Point(xy) for xy in zip(gp2_df["longitude_dec"], gp2_df["latitude_dec"])]
    gp2_data = gpd.GeoDataFrame(gp2_df, geometry = geometry)
    gp2_data.set_crs(epsg = 4326, inplace = True)
    gp2_data = gp2_data.to_crs(epsg = epsg_code)
    gp2_data = gp2_data.rename(columns={
            "longitude_dec": "longitude",
            "latitude_dec": "latitude",
            }
        )
    gp2_data_columns = {
        "trace": "int64",
        "time_elapsed_s": "float64",
        "antenna_altitude_above_ground_m": "float64",
        "datetime_utc": "datetime64[ns, UTC]",
        "longitude": "float64",
        "latitude": "float64",
        "geometry": "geometry"
        }
    gp2_data = cast(gpd.GeoDataFrame, adjust_column_types(gp2_data, gp2_data_columns))

    return gp2_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def fill_missing_traces(gnss_data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Identifies missing trace numbers and fills them with linearly interpolated values.

    Args:
        gnss_data - gpd.GeoDataFrame: DataFrame with 'traces' column and other GPS data

    Returns:
       gnss_data_filled - gpd.GeoDataFrame: DataFrame with missing traces filled via linear interpolation
    """
    # Ensure traces is sorted
    gnss_crs = gnss_data.crs
    gnss_data = gnss_data.sort_values("trace").reset_index(drop=True)

    # Find the full range of traces that should exist
    min_trace = gnss_data["trace"].min()
    max_trace = gnss_data["trace"].max()
    # Create a complete trace sequence
    complete_traces = pd.DataFrame({"trace": range(min_trace, max_trace + 1)})
    # Merge with existing data to identify missing traces
    gnss_data_filled = complete_traces.merge(gnss_data, on=["trace"], how = "left")

    # Check for existing columns
    if not "geometry" in gnss_data_filled.columns:
        raise ValueError("Geometry column not found.")
    elif not "datetime_utc" in gnss_data_filled.columns:
        raise ValueError("datetime_utc column not found.")

    # Handle datetime column separately first
    if "datetime_utc" in gnss_data_filled.columns:
        # Convert datetime to int64 using astype instead of view
        gnss_data_filled["datetime_numeric"] = pd.to_numeric(gnss_data_filled["datetime_utc"])

        # Replace the minimum int64 value (NaT converted) with NaN so it can be interpolated
        gnss_data_filled["datetime_numeric"] = gnss_data_filled["datetime_numeric"].replace(pd.NaT.value, np.nan)

        # Interpolate numeric values
        gnss_data_filled["datetime_numeric"] = gnss_data_filled["datetime_numeric"].interpolate(method = "linear")

        # Convert back to datetime with UTC timezone
        gnss_data_filled["datetime_utc"] = pd.to_datetime(gnss_data_filled["datetime_numeric"], unit = "ns", utc = True)
        gnss_data_filled = gnss_data_filled.drop(columns = ["datetime_numeric"])

    # Interpolate all numeric columns linearly, for that we need to extract the x and y values of our points first
    gnss_data_filled["x"] = gnss_data_filled["geometry"].apply(lambda geom: geom.x if geom else np.nan)
    gnss_data_filled["y"] = gnss_data_filled["geometry"].apply(lambda geom: geom.y if geom else np.nan)
    numeric_columns = gnss_data_filled.select_dtypes(include=["float64", "int64"]).columns
    numeric_columns = [col for col in numeric_columns if col != "trace"]
    # Interpolate linearly
    for col in numeric_columns:
        gnss_data_filled[col] = gnss_data_filled[col].interpolate(method="linear")
    # Get the points into the geometry
    gnss_data_filled["geometry"] = gpd.points_from_xy(gnss_data_filled["x"], gnss_data_filled["y"])
    # Drop the x and y column
    gnss_data_filled = gnss_data_filled.drop(columns=["x", "y"])
    # Ensure that the output is an gdf
    gnss_data_filled = gpd.GeoDataFrame(gnss_data_filled, geometry = "geometry", crs = gnss_crs)

    return gnss_data_filled

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def get_transect_info_from_file_stem(file_stem: str) -> Tuple[Union[gpd.GeoDataFrame, None], Union[gpd.GeoDataFrame, None]]:
    """
    Extracts transect information from a transect name string.

    Args:
        gnss_file_stem - str: The file stem

    Returns:
        transect_start_id, transect_end_id - str: start and end point IDs.
    """
    cleaned_gps_control_points = load_control_points()
    transect_info = file_stem.split("_")
    if "IWP" in transect_info[2]:
        transect_start = "IWP-" + transect_info[2].split("-")[1]
        transect_end = "IWP-" + transect_info[2].split("-")[2]
    elif "Siksik" in transect_info[2]:
        transect_start = transect_info[2] + "-Start"
        transect_end = transect_info[2] + "-End"
    else:
        raise ValueError(f"Transect name format unknown: {transect_info}")

    if "S-E" in transect_info[3]:
        transect_start_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_start].iloc[0:1]
        transect_end_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_end].iloc[0:1]
    elif "E-S" in transect_info[3]:
        transect_start_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_end].iloc[0:1]
        transect_end_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_start].iloc[0:1]
    elif "S-C" in transect_info[3]:
        transect_start_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_start].iloc[0:1]
        transect_end_id = None
    elif "C-S" in transect_info[3]:
        transect_start_id = None
        transect_end_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_start].iloc[0:1]
    elif "E-C" in transect_info[3]:
        transect_start_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_end].iloc[0:1]
        transect_end_id = None
    elif "C-E" in transect_info[3]:
        transect_start_id = None
        transect_end_id = cleaned_gps_control_points[cleaned_gps_control_points["study_site_id"] == transect_end].iloc[0:1]
    else:
        raise ValueError(f"Transect direction unknown in transect name: {transect_info}")

    if transect_start_id is not None:
        transect_start_id.reset_index()

    if transect_end_id is not None:
        transect_end_id.reset_index()

    return transect_start_id, transect_end_id

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def correct_gnss_with_rtk(gnss_data: gpd.GeoDataFrame, file_stem: str, epsg_code: int = 3155) -> gpd.GeoDataFrame:
    """
    Corrects the gnss data using rtk control points.

    Args:
        gnss_data - gpd.GeoDataFrame: GNSS data
        file_stemh - str: The file stem that referes to the data
        epsg_code - int: EPSG code. Defaults to 3155
    Returns:
        gnss_data_corr - gpd.GeoDataFrame: GNSS data corrected by RTK points
    """
    # Load RTK points
    gnss_start, gnss_end = get_transect_info_from_file_stem(file_stem)
    # Check transect_start_id and transect_end_id
    if gnss_start is None and gnss_end is None:
        raise ValueError("Neither start nor end could be identified.")
    # ----------------------------------------------------------------------------------------------- #
    if gnss_start is not None and gnss_end is not None:
        distance_start = geodesic((gnss_start["latitude"].item(), gnss_start["longitude"].item()),
                            (gnss_data.iloc[0]["latitude"], gnss_data.iloc[0]["longitude"])
                            ).meters
        distance_end = geodesic((gnss_end["latitude"].item(), gnss_end["longitude"].item()),
                            (gnss_data.iloc[-1]["latitude"], gnss_data.iloc[-1]["longitude"])
                            ).meters
        if distance_start > 1000 or distance_end > 1000:
            raise ValueError("Distnace too high and unrealistic!")

         # Apply linear interpolation correction
        offset_start_lon = gnss_start["longitude"].item() - gnss_data.iloc[0]["longitude"]
        offset_start_lat = gnss_start["latitude"].item() - gnss_data.iloc[0]["latitude"]
        offset_start_elev = gnss_start["elevation_m"].item() - gnss_data.iloc[0]["antenna_altitude_above_ground_m"]

        offset_end_lon = gnss_end["longitude"].item() - gnss_data.iloc[-1]["longitude"]
        offset_end_lat = gnss_end["latitude"].item() - gnss_data.iloc[-1]["latitude"]
        offset_end_elev = gnss_end["elevation_m"].item() - gnss_data.iloc[-1]["antenna_altitude_above_ground_m"]

        # Create interpolation weights (0 at start, 1 at end)
        weights = np.linspace(0, 1, len(gnss_data))

        # Apply linear interpolation of offsets
        offset_lon = offset_start_lon + weights * (offset_end_lon - offset_start_lon)
        offset_lat = offset_start_lat + weights * (offset_end_lat - offset_start_lat)
        offset_elev = offset_start_elev + weights * (offset_end_elev - offset_start_elev)
        # Apply corrections
        gnss_data["longitude"] = gnss_data["longitude"] + offset_lon
        gnss_data["latitude"] = gnss_data["latitude"] + offset_lat
        gnss_data["elevation_m"] = gnss_data["antenna_altitude_above_ground_m"] + offset_elev

    else:
        if gnss_start is not None and gnss_end is None:
            control_point = gnss_start

        elif gnss_end is not None and gnss_start is None:
            control_point = gnss_end

        distance_correction = geodesic(
                (control_point["latitude"].item(), control_point["longitude"].item()),
                (gnss_data.iloc[0]["latitude"], gnss_data.iloc[0]["longitude"])
                ).meters
        if distance_correction > 1000:
            raise ValueError("Distnace too high and unrealistic!")

        offset_lon = control_point["longitude"].item() - gnss_data.iloc[0]["longitude"]
        offset_lat = control_point["latitude"].item() - gnss_data.iloc[0]["latitude"]
        offset_elev = control_point["elevation_m"].item() - gnss_data.iloc[0]["antenna_altitude_above_ground_m"]
        # Apply same offset to all points
        gnss_data["longitude"] = gnss_data["longitude"] + offset_lon
        gnss_data["latitude"] = gnss_data["latitude"] + offset_lat
        gnss_data["elevation_m"] = gnss_data["antenna_altitude_above_ground_m"] + offset_elev

    # Get the points into the geometry
    gnss_data["geometry"] = gnss_data.apply(lambda row: Point(row["longitude"], row["latitude"]), axis = 1)
    gnss_data = gpd.GeoDataFrame(gnss_data, geometry="geometry", crs="EPSG:4326").to_crs(epsg_code)
    # Drop the x and y column
    gnss_data = gnss_data.drop(columns=["antenna_altitude_above_ground_m"])
    # Ensure that the output is an gdf
    # gnss_data = gpd.GeoDataFrame(gnss_data, geometry = "geometry", crs = gnss_crs)
    gnss_data_columns = {
        "trace": "int64",
        "time_elapsed_s": "float64",
        "datetime_utc": "datetime64[ns, UTC]",
        "elevation_m": "float64",
        "longitude": "float64",
        "latitude": "float64",
        "geometry": "geometry"
        }
    gnss_data = cast(gpd.GeoDataFrame, adjust_column_types(gnss_data, gnss_data_columns))
    return gnss_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
