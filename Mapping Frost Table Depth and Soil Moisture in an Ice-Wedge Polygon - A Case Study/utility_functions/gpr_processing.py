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

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-06
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment import *
from utility_functions.gnss_handling import load_gp2_data, fill_missing_traces, correct_gnss_with_rtk
from utility_functions.general import adjust_column_types
from utility_functions.combine_tifs import get_combined_raster
from utility_functions.active_layer_thickness import load_active_layer_data
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def crop_transect_data(gdf: gpd.GeoDataFrame, pck_file: Path, ) -> tuple[int, int]:
    """
    This function loads the cropping information for the given SEG-Y file from the corresponding .dat file in the subtransects folder.
    It determines the start and end trace indices for cropping based on the information in the .dat file and the trace numbers in the transect_data GeoDataFrame.
    If no cropping information is found, it returns the minimum and maximum trace numbers from the transect_data GeoDataFrame.
    Args:
        base_path - Path: Root path of the whole project
        pck_file - Path: Path to the pick file
        transect_data - gpd.GeoDataFrame: GeoDataFrame containing the transect data

    Returns:
        start_trace, end_trace - Tuple[int, int]: Start and end trace indices for cropping.
    """
    # Load cropping information from subtransect folder
    cropping_info_path = manual_input_folder / "gpr_analysis" / "Subtransects" / Path(pck_file.stem).with_suffix(".dat")
    if cropping_info_path.exists():
        cropping_info_df = pd.read_csv(cropping_info_path, sep = "\t", names = ["lower_crop", "upper_crop"])
        if not cropping_info_df.empty:
            # The cropping info lists the start and end points of the removed sections related to the traces.
            # This cropping is the same input as giving in ReflexW EditTraces/TraceRanges -> remove
            # We only have to tell the function the start and end trace that we want to remove. If we just want to remove the beginning or the end,
            # the input is only one row
            if len(cropping_info_df) == 1:
                if cropping_info_df.iloc[0]["lower_crop"] == 0:
                    start_trace = cropping_info_df.iloc[0]["upper_crop"]
                    end_trace = gdf["trace"].max()
                elif cropping_info_df.iloc[0]["upper_crop"] == gdf["trace"].max():
                    start_trace = 0
                    end_trace = cropping_info_df.iloc[0]["lower_crop"]
                else:
                    raise ValueError("The cropping info file has only one row, but the cropping is not at the beginning or the end of the transect. Please check the cropping info file.")
            elif len(cropping_info_df) == 2:
                # If there are two rows, we assume that the cropping is in the middle of the transect and we have to remove the section between the upper crop of the first row and the lower crop of the second row
                start_trace = cropping_info_df["upper_crop"].min()
                end_trace = cropping_info_df["lower_crop"].max()
            else:
                raise ValueError("The cropping info file has more than two rows. Please check the cropping info file.")
        # If the cropping info file is empty, we assume that there is no cropping and we use the full transect
        else:
            print(f"Warning: Cropping info file {cropping_info_path} is empty. Using full transect.")
            start_trace = gdf["trace"].min()
            end_trace = gdf["trace"].max()
    # If there is no cropping info file, we assume that there is no cropping and we use the full transect
    else:
        print(f"Warning: No cropping info file found at {cropping_info_path}. Using full transect.")
        start_trace = gdf["trace"].min()
        end_trace = gdf["trace"].max()
    # Return the start and end trace as integers
    return int(start_trace), int(end_trace)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def add_pick_line(gdf: gpd.GeoDataFrame, pck_file: Path, used_on_iwp: bool) -> gpd.GeoDataFrame:
    """
    Loads the reflection line picks from the matching PCK file for the given SEG-Y file.
    If IWP: Cut start and ends that are not in the pick line.
    If not IWP: Classify pick line as identified hummock.
    Args:
        gdf - gpd.GeoDataFrame: DataFrame where the pick line is added to.
        pck_file - Path: Path to the PCK file
        used_on_iwp - boolean: IWP processing identifier.
    Returns:
        gdf_with_pck - gpd.GeoDataFrame: DataFrame containing reflection line picks
    """
    if not pck_file.exists():
        raise FileNotFoundError(f"PCK file not found at {pck_file}. Please ensure that the PCK file exists and the path is correct.")

    # We now should have found the matching PCK file
    column_names = ["trace",         # place 1
                    "refl_line_profile_distance",     # place 2
                    "refl_line_travel_times_ns",         # place 3
                    "refl_line_depths",               # place 4
                    "refl_line_elevations",           # place 5
                    "refl_line_amplitudes",           # place 6
                    "refl_line_velocities",           # place 7
                    "refl_line_pick_codes",           # place 8
                    "refl_line_original_filenames",   # place 9
                    "refl_line_shot_x_pos",           # place 10
                    "refl_line_shot_y_pos",           # place 11
                    "refl_line_shot_z_pos",           # place 12
                    "refl_line_rec_x_pos",            # place 13
                    "refl_line_rec_y_pos",            # place 14
                    "refl_line_rec_z_pos"             # place 15
                    ]
    reflection_line_df = pd.read_csv(pck_file, sep = "\t", names = column_names)[["trace", "refl_line_travel_times_ns"]]
    # Load start and end traces to align the pick file correctly
    start_trace, end_trace = crop_transect_data(
        gdf = gdf,
        pck_file = pck_file
        )
    if start_trace > end_trace:
        raise ValueError(f"Invalid cropping information: start trace ({start_trace}) is greater than end trace ({end_trace}). Please check the cropping info file.")

    # Determine start and end trace if not provided
    if start_trace == gdf["trace"].min() and end_trace == gdf["trace"].max():
        reflection_line_df["trace"] = reflection_line_df["trace"]
    else:
        reflection_line_df["trace"] = reflection_line_df["trace"] + start_trace

    gdf_with_pck = gdf.merge(
        reflection_line_df[["trace", "refl_line_travel_times_ns"]],
        on = "trace",
        how = "left"
        )

     # Crop the transect data based on the determined start and end trace
    before_crop_len = len(gdf_with_pck)
    gdf_with_pck = gdf_with_pck[(gdf_with_pck["trace"] >= start_trace) & (gdf_with_pck["trace"] <= end_trace)].reset_index(drop=True)

    if used_on_iwp == True:
        # As the IWP should have a continous pick line, we want to remove missing picks at the beginning and the end of the transect,
        # but keep them in the middle, as they might be relevant for the interpretation of the radiogram.
        first_valid_index = gdf_with_pck["refl_line_travel_times_ns"].first_valid_index()
        last_valid_index = gdf_with_pck["refl_line_travel_times_ns"].last_valid_index()
        gdf_with_pck = gdf_with_pck.loc[first_valid_index:last_valid_index].reset_index(drop = True)
    else:
        gdf_with_pck["is_hummock"] = False
        gdf_with_pck.loc[gdf_with_pck["refl_line_travel_times_ns"].notna(), "is_hummock"] = True

    after_crop_len = len(gdf_with_pck)
    if before_crop_len != after_crop_len and used_on_iwp == False:
        gdf_with_pck["transect_cropped"] = True
    else:
        gdf_with_pck["transect_cropped"] = False
    return gdf_with_pck

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_sgy_trace(sgy_file: Path) -> Tuple[np.ndarray, float]:
    """
    Loads GPR trace data from a SEG-Y file.

    Args:
        sgy_path: Path to the SEG-Y file

    Returns:
        data: 2D numpy array of GPR traces (samples x traces)
    """
    with segyio.open(sgy_file, "r", ignore_geometry = True) as f:
        data = segyio.tools.collect(f.trace[:]).T

        dt_ns = segyio.dt(f) / 1000  # convert picoseconds to nanoseconds (ns)
    return data, dt_ns

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_gnss_data(epsg_code: int = 3155) -> gpd.GeoDataFrame:
    """
    Loads or generates the gnss data file containing all found transects

    Args:
        epsg_code - int: Wanted epsg code, Optional, defaults to 3155

    Returns:
        gnss_data - gpd.GeoDataFrame: Containing the transect information of all used transects.
    """
    gnss_data_file = results_folder / "cleaned_data" / Path(f"gnss_traces_of_all_gpr_transects_in_EPSG{epsg_code}").with_suffix(".parquet")
    if gnss_data_file.exists():
        gnss_data = gpd.read_parquet(gnss_data_file)
    else:
        import_folder = coding_folder / "gpr_analysis" / "ASCII" / "Import"
        gp2_files = list(import_folder.rglob("*.gp2"))

        gp2_collector = []
        for gp2_file in gp2_files:
            print(f"Loading {gp2_file}.")
            # Load data from gp2 file
            gp2 = load_gp2_data(
                gp2_path = gp2_file,
                epsg_code = epsg_code
                )
            gp2 = fill_missing_traces(
                gnss_data = gp2
                )
            gp2 = correct_gnss_with_rtk(
                gnss_data = gp2,
                file_stem = gp2_file.stem,
                epsg_code = 3155
                )
            # Load information for hd file
            head = pd.read_csv(
                Path(gp2_file).with_suffix(".hd"),
                skiprows = 3,
                nrows = 7,
                header = None
                )
            starting_position = float(head.loc[head[0].str.contains("STARTING POSITION", na = False), 0].iloc[0].split("=")[1].strip())
            final_position = float(head.loc[head[0].str.contains("FINAL POSITION", na = False), 0].iloc[0].split("=")[1].strip())
            number_of_traces = int(head.loc[head[0].str.contains("NUMBER OF TRACES", na = False), 0].iloc[0].split("=")[1].strip())
            # Use header information to calculate trace increment
            trace_increment_m = (final_position - starting_position)/number_of_traces

            # Add "distance_from_starting_pos_m", "transect_name", and "elevation_m_time_delay_ns"
            gp2["distance_from_starting_pos_m"] = gp2["trace"] * trace_increment_m + starting_position
            gp2["transect_name"] = gp2_file.stem
            gp2["elevation_m_time_delay_ns"] = 2 * (gp2["elevation_m"].max() - gp2["elevation_m"]) / (speed_of_light * 1e-9)

            # Append to list
            gp2_collector.append(gp2)

        # Merge gp2_collector into one gdf
        for gp2 in gp2_collector:
            if gp2.crs != CRS.from_epsg(epsg_code):
                raise ValueError(f"EPSG mismatch found for {gp2['transect_name'][0].item()}")
        # Concat data and ensure column types
        gnss_data = pd.concat(gp2_collector, ignore_index = True)
        gnss_data_columns = {
            "trace": "int64",
            "time_elapsed_s": "float64",
            "datetime_utc": "datetime64[ns, UTC]",
            "elevation_m": "float64",
            "distance_from_starting_pos_m": "float64",
            "transect_name": "string",
            "elevation_m_time_delay_ns": "float64",
            "geometry": "geometry"
            }
        gnss_data = cast(gpd.GeoDataFrame, adjust_column_types(gnss_data, gnss_data_columns))
        # Save as parquet file
        gnss_data.to_parquet(gnss_data_file)
    return gnss_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_transect_area_from_tifs(tif_files: dict, transect_data: gpd.GeoDataFrame, cut_half_width_m: float = 5.0, epsg_code: int = 3155) -> Tuple[gpd.GeoDataFrame, dict]:
    """
    Cuts out and rotates transect areas from orthomosaic TIFF files based on GPS data.
    The function extracts a rectangular area around the transect defined by GPS points, rotates it to align with the transect direction, and returns the resulting image and metadata.
    Args:
        tif_files - dict: List of dictionaries containing TIFF file paths and resampling methods and wanted bands
        transect_data - gpd.GeoDataFrame: Data of the transect to process
        cut_half_width_m - float: half width in meters to include around transect. Optional, defaults to 5
        epsg_code - int: EPSG code. Defaults to 3155
    Returns:
        transect_data - gpd.DataFrame: GPS data for the transect
        image_info - dict: Information about the rotated image and GPS coordinates
    """

    # ------------------------------------------------------------------------------------------------ #
    # ------------------------------- #
    # Get the combined tif file.
    # This will reproject and resample the input tifs to the same CRS and resolution and combine them into one multi-band raster file.
    # If the combined file already exists, it will be loaded directly.
    buffer_size_m = cut_half_width_m * 7.5
    combined_tif_file, sorted_rasters = get_combined_raster(
        input_rasters = tif_files,
        target_epsg = epsg_code,
        target_resolution = "highest",
        ensure_equal_resolution = False,
        buffer_size_m = buffer_size_m
        )

    # ------------------------------------------------------------------------------------------------ #
    # ------------------------------- #
    # The file exists, so now we can load and cut
    # ------------------------------- #
    # Load the data

    with rasterio.open(combined_tif_file) as src:
        # Verify the CRS of the TIFF file
        if src.crs is None:
            raise ValueError("Raster CRS is undefined.")

        # Sanity check: Ensure the transect GPS data and the TIFF file are in the same CRS
        # This should always be the case. If not, it indicates a problem with the data preparation steps.
        if transect_data.crs != src.crs:
             raise ValueError(f"CRS mismatch: Transect CRS is {transect_data.crs}, but TIFF CRS is {src.crs.to_epsg()}. Please ensure both are in the same projected CRS.")

        # Select the transect GPS points and transform them to the TIFF CRS
        transect_lons = transect_data.geometry.x.values
        transect_lats = transect_data.geometry.y.values
        transformer = Transformer.from_crs(transect_data.crs, src.crs, always_xy=True)
        x_i, y_i = transformer.transform(transect_lons.tolist(), transect_lats.tolist())

        # Get the start and end points of the transect in the TIFF CRS
        tsx, tsy, tex, tey = x_i[0], y_i[0], x_i[-1], y_i[-1]
        # Check whether they are actually the outermost points in the transects
        if not (np.isclose(tsx, x_i).any() and np.isclose(tsy, y_i).any() and np.isclose(tex, x_i).any() and np.isclose(tey, y_i).any()):
            raise ValueError("Start and end points of the transect are not the most outer points in the transect GPS data. Please check the GPS data for the transect.")

        # Calculate transect angle and rotation needed to align transect horizontally
        transect_vector_x = tex - tsx
        transect_vector_y = tey - tsy
        transect_angle = np.arctan2(transect_vector_y, transect_vector_x)

        # Expand bounds to ensure rotated image fits
        minx = np.min(x_i) - buffer_size_m
        maxx = np.max(x_i) + buffer_size_m
        miny = np.min(y_i) - buffer_size_m
        maxy = np.max(y_i) + buffer_size_m

        # Load the data from the tif file
        window = rasterio.windows.from_bounds(minx, miny, maxx, maxy, src.transform)
        data = src.read(window = window)
        window_transform = src.window_transform(window)

        # -------------------- #
        # Compute extent centered on rotation center (meters)
        pixel_size = abs(window_transform.a)
        center_x = (minx + maxx) / 2
        center_y = (miny + maxy) / 2

        # Transform GPS coords into rotated (transect-aligned) space
        cos_a = np.cos(transect_angle)
        sin_a = np.sin(transect_angle)
        transformed_x_i = (x_i - center_x) * cos_a + (y_i - center_y) * sin_a
        transformed_y_i = -(x_i - center_x) * sin_a + (y_i - center_y) * cos_a

        # -------------------- #
        # Rotate extracted window so transect is horizontal
        transect_angle_deg = np.degrees(transect_angle)
        rotated_bands = []
        # Raster bands start at 1, but our data array starts at 0, so we need to keep track of the band numbers across the different rasters.
        start_band = -1
        # Treat the different bands depending on the resampling method
        for raster_info in sorted_rasters:
            bands = np.array(raster_info["bands"]) + start_band
            for band in bands:
                rotated_band = ndimage_rotate(data[band], -transect_angle_deg, reshape = True, order = raster_info["resampling"].value)
                rotated_bands.append(rotated_band)
            start_band += len(bands)

        # Combine the rotated bands into one array and calculate the new extent after rotation
        rot_data = np.array(rotated_bands)  # shape: (bands, h, w)
        rotated_h, rotated_w = rot_data.shape[1], rot_data.shape[2]

        # Calculate the new extent of the rotated image in meters, centered on the rotation center
        x0 = - rotated_w * pixel_size / 2
        x1 = rotated_w * pixel_size / 2
        y0 = - rotated_h * pixel_size / 2
        y1 = rotated_h * pixel_size / 2
        rotated_full_extent = [x0, x1, y0, y1]

        # Calculate pixel coordinates of GPS points in the rotated space
        pixel_x = ((transformed_x_i - x0) / pixel_size).astype(int)
        pixel_y = ((transformed_y_i - y0) / pixel_size).astype(int)


        start_band = -1
        # Go through the raster info and add the rotated data to the raster info dictionary.
        for raster_info in sorted_rasters:
            bands = (np.array(raster_info["bands"]) + start_band).tolist()
            # For easier handling:
            # If there is only one band, we can store it as a 2D array. If there are multiple bands, we store them as a 3D array with the band dimension last (h, w, bands).
            if len(bands) == 1:
                raster_info["img_data"] = rot_data[bands[0]]
            else:
                raster_info["img_data"] = np.transpose(rot_data[bands], (1, 2, 0))
            start_band += len(bands)

    # Sanity check: Ensure the number of GPS points matches the number of transformed coordinates
    if len(transect_data) != len(transformed_x_i) or len(transect_data) != len(transformed_y_i):
        raise ValueError("Length of transect GPS data does not match length of transformed GPS coordinates. Please check the GPS data and transformations.")
    else:
        transect_data.loc[:, "transect_relative_x_gps_coordinate_m"] = transformed_x_i
        transect_data.loc[:, "transect_relative_y_gps_coordinate_m"] = transformed_y_i

    # Pack everything into a dictionary for easier handling in the next steps.
    image_info = {}
    for raster_info in sorted_rasters:
        image_info[raster_info["name"]] = {
            "img_data": raster_info["img_data"],
            "bands": raster_info["bands"],
            "resampling": raster_info["resampling"],
            "path": raster_info["path"],
            "mapping_style": raster_info["mapping_style"],
            "label": raster_info["label"]
            }
    image_info["rotational_info"] = {
        "transect_angle": transect_angle,
        "center_x": center_x,
        "center_y": center_y,
        "rotated_full_extent": rotated_full_extent
        }

    print("Loaded and rotated transect area from TIFF file successfully loaded gps data.")
    print("--------------------------------------------------------------------------------")
    return transect_data, image_info

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def combine_gpr_gnss_and_load_tif_file(sgy_file: Path, tif_files: dict, cut_half_width_m: float) -> Tuple[gpd.GeoDataFrame, dict]:
    """
    This function combines GPR data and GPS data in a geospatial dataframe joining on the trace indices.
    It also renames the "traces" column in "trace" and resets the index.

    Furthermore, it loads the orthomosaic data for the specified transect, cutting out the area around the transect.
    It also exports the roational information of the transect.

    Args:
        sgy_path - Path: Path to the SEG-Y file
        tif_files - dict: List of dictionaries containing TIFF file paths and resampling methods and wanted bands
        cut_half_width_m - float: Half width in meters to include around transect

    Returns:
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
        rotational_info - dict: Dictionary containing transect angle and center coordinates
    """

    # ------------------------------------------------------------------------------------------------ #
    # ------------------------------- #
    # Load gps data, either we generate it or we load it from the parquet file
    transect_name = re.sub(r"_H_.*", "", sgy_file.stem.replace("HZ", "Hz").replace("SIKSIK", "Siksik").replace("LOWER", "Lower").replace("MIDDLE", "Middle").replace("UPPER", "Upper"))
    transect_data = load_gnss_data(
        epsg_code = 3155
        )
    # Select the transect needed
    mask = transect_data["transect_name"] == transect_name
    if not mask.any():
        raise ValueError(f"{transect_name} not found.")
    transect_data = transect_data[mask].reset_index(drop=True)

    # Load subset of tif data for transect area, get GPS data, and transect realtive coordinates in transect-aligned space
    transect_data, image_data = load_transect_area_from_tifs(
        tif_files = tif_files,
        transect_data = transect_data,
        cut_half_width_m = cut_half_width_m,
        epsg_code = 3155
        )

    # Load GPR data
    data, dt_ns = load_sgy_trace(sgy_file)

    # Combine GPR and GPS data
    if not "trace_values" in transect_data.columns:
        transect_data["trace_values"] = data.T.tolist()
    if not "dt_ns" in transect_data.columns:
        transect_data["dt_ns"] = dt_ns

    return transect_data, image_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_values_from_tif_file(tif_file: Path, gdf: gpd.GeoDataFrame, new_col_name: Union[str, None] = None, band_idx: int = 1) -> gpd.GeoDataFrame:
    """
    Loads values from a TIFF file at specified x and y coordinates.

    Args:
        tif_path - Path: The path to the TIFF file.
        gdf - gpd.GeoDataFrame: A GeoDataFrame containing the x and y coordinates.
        new_col_name - str: The name of the new column to be added to the GeoDataFrame with the sampled values.
        band_idx - int: The index of the band to be sampled.

    Returns:
        gdf - gpd.GeoDataFrame: The GeoDataFrame with the sampled values added as a new column.
    """
    # Load the TIFF file using rioxarray
    rds = cast(xr.DataArray, rioxarray.open_rasterio(tif_file, engine="rasterio", masked=True))
    raster_crs = rds.rio.crs
    # Check CRS of gdf and tif, reproject if necessary
    if gdf.crs != raster_crs:
        gdf = gdf.to_crs(raster_crs)

    # Sample the raster values at the x and y coordinates from the GeoDataFrame
    x_coords_da = xr.DataArray(gdf.geometry.x.values, dims = "z")
    y_coords_da = xr.DataArray(gdf.geometry.y.values, dims = "z")
    # Reading out the values at the specified coordinates using nearest neighbor interpolation
    if rds.rio.count == 1:
        # If there is only one band, we ignore the band index and just read the values from that single band
        sampled_values = rds.sel(x = x_coords_da, y = y_coords_da, method = "nearest").values[0]
    else:
        print(f"Retrieved values from band {band_idx} from {tif_file.name} for {len(gdf)} points.")
        sampled_values = rds.sel(x = x_coords_da, y = y_coords_da, method = "nearest").values[band_idx-1]
    if new_col_name is not None:
        new_col_name = new_col_name

    else:
        new_col_name = f"{tif_file.stem}_values"
    gdf[new_col_name] = sampled_values
    gdf.loc[:, new_col_name] = gdf.loc[:, new_col_name].replace({np.nan: 0})
    return gdf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def add_active_layer_thickness_to_transect_data(sgy_stem: str,  transect_data: gpd.GeoDataFrame, used_velocities_m_ns: dict, rotational_info: dict, sampling_period: list, drop_frozen_table_measurements: Union[np.ndarray, None] = None, epsg_code: int = 3155) -> gpd.GeoDataFrame:
    """
    This function adds the active layer thickness data to the transect data GeoDataFrame.
    It selects active layer data points within a specified buffer radius around the transect,
    filters them by date and study site ID, and maps the active layer thickness data to the nearest transect points.

    Args:
        sgy_stem - str: Path stem to the SEG-Y file
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
        used_velocities_m_ns - dict: Dictionary of velocities used to convert active layer thickness from meters to nanoseconds
        rotational_info - dict: Dictionary containing transect angle and center coordinates
        sampling_period - list: List of start and end date for when to sample
        epsg_code - int: Code of the EPSG unit. Defaults to 3155
    Returns:
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR, GPS, and active layer data
    """
    # Get study_site_id
    study_site_id = sgy_stem.split("_")[2].replace("SIKSIK-", "Siksik-").replace("LOWER", "Lower").replace("MIDDLE", "Middle").replace("UPPER", "Upper")

    # Load active layer data and ensure correct projection
    active_layer_thickness = load_active_layer_data().to_crs(32608)

    # Filter data by using study site and time constraints
    alt_selection = active_layer_thickness[
        (active_layer_thickness["study_site_id"] == study_site_id) &
        (active_layer_thickness["datetime_utc"] >= sampling_period[0]) &
        (active_layer_thickness["datetime_utc"] <= sampling_period[1])
        ].copy()
    if alt_selection.empty:
        raise ValueError("No active layer data found.")

    # Drop duplicate measurement numbers to ensure one-to-one mapping, drop unneeded columns, and rename other ones
    alt_selection = alt_selection.drop_duplicates(subset = ["measurement_number"]).reset_index(drop = True)
    alt_selection.drop(columns = ["datetime_utc", "negative_active_layer_length_cm", "active_layer_probe_length_cm"], inplace=True)
    alt_selection = alt_selection.rename(columns = {
        col: f"alt_data_{col}"
        for col in alt_selection.columns
        if not col.startswith("active_layer") and col != "geometry"
        })
    # Save geometry in extra cols and add velocities
    alt_selection["alt_data_x"] = alt_selection.geometry.x
    alt_selection["alt_data_y"] = alt_selection.geometry.y
    for vel_key, used_velocity_info in used_velocities_m_ns.items():
        alt_selection[f"alt_for_{vel_key}_ns"] = (2 * alt_selection["active_layer_thickness_m"] / used_velocity_info[0]) # two-way travel time
    # Calculate rotated system
    cos_a = np.cos(rotational_info["transect_angle"])
    sin_a = np.sin(rotational_info["transect_angle"])
    alt_selection["alt_data_transect_relative_x"] = (alt_selection["alt_data_x"] - rotational_info["center_x"]) * cos_a + (alt_selection["alt_data_y"] - rotational_info["center_y"]) * sin_a
    alt_selection["alt_data_transect_relative_y"] = -(alt_selection["alt_data_x"] - rotational_info["center_x"]) * sin_a + (alt_selection["alt_data_y"] - rotational_info["center_y"]) * cos_a

    # Also ensure same projection for the transect data
    transect_data = transect_data.to_crs(32608)

    # For each active layer point, find the nearest transect_data point and assign values
    nearest_indices = alt_selection.geometry.apply(lambda geom: transect_data.geometry.distance(geom).idxmin())
    for idx, nearest_idx in enumerate(nearest_indices):
        for col in alt_selection.columns:
            if col == "active_layer_thickness_m":
                transect_data.at[nearest_idx, "active_layer_thickness_m"] = alt_selection.iloc[idx]["active_layer_thickness_m"]
            elif col == "geometry":
                continue
            else:
                 transect_data.at[nearest_idx, col] = alt_selection.iloc[idx][col]
    if drop_frozen_table_measurements is not None:
        alt_cols = list(alt_selection.columns.difference(["geometry"])) + ["distance_to_alt_data"]
        for drop_range in drop_frozen_table_measurements:
            transect_data.loc[(transect_data["distance_from_starting_pos_m"] >= drop_range[0]) & (transect_data["distance_from_starting_pos_m"] <= drop_range[1]), alt_cols] = np.nan

    transect_data = transect_data.to_crs(3155)
    return transect_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def add_nearest_non_nan_info(df: gpd.GeoDataFrame, value_col: str, distance_col: str = "distance_from_starting_pos_m") -> tuple[gpd.GeoDataFrame, str, str, str, str, str]:
    """
    Adds columns with the distance, index, and value of the nearest non-NaN measurement.

    Args:
        df - gpd.GeoDataFrame): Input DataFrame.
        value_col - str, optional: Name of the measurement column.
        distance_col - str, optional: Name of the distance column. Defaults to "distance_from_starting_pos_m".
    Returns:
        df - gpd.GeoDataFrame: DataFrame with three new columns.
        distance_to_nearest_col - str: Name of the new column with distances to nearest non-NaN.
        index_of_nearest_col - str: Name of the new column with indices of nearest non-NaN.
        value_of_nearest_col - str: Name of the new column with values of nearest non-NaN.
        distance_ratio_col - str: Name of the new column with distance ratios to nearest non-NaN.
        max_distance_col - str: Name of the new column with maximum distances for each group of identical nearest non-NaN values.
    """
    # Get indices and distances of non-NaN values
    non_nan_mask = df[value_col].notna()
    non_nan_indices = np.where(non_nan_mask)[0]
    non_nan_distances = df.loc[non_nan_indices, distance_col].values

    distance_to_nearest = np.empty(len(df))
    index_of_nearest = np.empty(len(df), dtype=int)
    value_of_nearest = np.empty(len(df))

    for i, d in enumerate(df[distance_col].values):
        if len(non_nan_distances) == 0:
            distance_to_nearest[i] = np.nan
            index_of_nearest[i] = -1
            value_of_nearest[i] = np.nan
        else:
            idx = np.argmin(np.abs(non_nan_distances - d))
            distance_to_nearest[i] = np.abs(non_nan_distances[idx] - d)
            index_of_nearest[i] = non_nan_indices[idx]
            value_of_nearest[i] = non_nan_distances[idx]  # <-- returns the distance
    distance_to_nearest_non_nan_col = "distance_to_nearest_non_nan_selected_on_" + value_col
    distance_ratio_col = "distance_ratio_to_nearest_non_nan_for_" + value_col
    max_distance_col = "max_distance_for_" + value_col
    index_of_nearest_non_nan_col = "index_of_nearest_non_nan_for_" + value_col
    value_of_nearest_non_nan_col = f"value_of_{distance_col}_from_nearest_non_nan_for_" + value_col

    df[distance_to_nearest_non_nan_col] = distance_to_nearest
    df[max_distance_col] = np.nan
    df[index_of_nearest_non_nan_col] = index_of_nearest
    df[value_of_nearest_non_nan_col] = value_of_nearest
    df[distance_ratio_col] = np.nan
    # Calculate distance ratio within groups of identical values in value_of_nearest_col
    grp_df = df.groupby(index_of_nearest_non_nan_col)
    for _, group in grp_df:
        max_distance = np.abs(group[distance_to_nearest_non_nan_col]).max()
        if max_distance == 0:
            df.loc[group.index, distance_ratio_col] = np.nan
        else:
            df.loc[group.index, distance_ratio_col] = group[distance_to_nearest_non_nan_col] / max_distance
            df.loc[group.index, max_distance_col] = max_distance
    return df, distance_to_nearest_non_nan_col, index_of_nearest_non_nan_col, value_of_nearest_non_nan_col, distance_ratio_col, max_distance_col

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def calculate_ground_velocities(gdf: gpd.GeoDataFrame, feature_correction: Union[dict, None], used_velocities: dict) -> gpd.GeoDataFrame:
    """
    Calcualtes ground velocities using estimated features and active layer data.

    Args:
        gdf - gpd.GeoDataFrame: Data Frame containing the used data.
        feature_correction - dict: Dictionary used for correction
        used_velocities - dict: Dictionary of used velocities
    Returns:
        data - gpd.GeoDataFrame: Data Frame with the calculated ground velocities
    """
    if not "wet" in used_velocities.keys() or not "moist" in used_velocities.keys() or not "dry" in used_velocities.keys():
        raise ValueError("Velocity keys not defined.")
    # Copy gdf
    data = gdf.copy()

    # Calculate the velocities based on the active layer thickness and reflection line travel times
    data["ground_truthed_velocities_m_ns"] = 2*data["active_layer_thickness_m"] / data["refl_line_travel_times_ns"]


    # If additional information is provided, use it to adjust the velocities for points with extreme anomalies
    # First we use the known velocities and add them to the estimated velocities
    data["estimated_velocities_m_ns"] = data["ground_truthed_velocities_m_ns"]
    if feature_correction is not None:
        # Now we go through our additional information (key by key) and add the estimated velocities
        # Additional information is a dictionary that contains an list of ranges (in distance from start of transect)
        # where the position of the minimum or maximum refl_line_travel_times_ns value shall be used to add an estimated velocity value
        for key, values in feature_correction.items():
            for value in values:
                # Skip all values that do not have exactly two entries (start and end)
                if len(value) != 2:
                    continue
                max_refl_line_travel_time_idx = data.loc[(data["distance_from_starting_pos_m"] >= value[0]) & (data["distance_from_starting_pos_m"] <= value[1])]["refl_line_travel_times_ns"].idxmax()
                min_refl_line_travel_time_idx = data.loc[(data["distance_from_starting_pos_m"] >= value[0]) & (data["distance_from_starting_pos_m"] <= value[1])]["refl_line_travel_times_ns"].idxmin()
                if "wet" in key:
                    data.loc[max_refl_line_travel_time_idx, "estimated_velocities_m_ns"] = used_velocities["wet"][0]
                elif "moist" in key:
                    data.loc[max_refl_line_travel_time_idx, "estimated_velocities_m_ns"] = used_velocities["moist"][0]
                elif "dry" in key:
                    data.loc[min_refl_line_travel_time_idx, "estimated_velocities_m_ns"] = used_velocities["dry"][0]

    # calculate the distance to the nearest point of each ground type
    data, distance_to_nearest_non_nan_col, index_of_nearest_non_nan_col, _, _, _ = add_nearest_non_nan_info(data, value_col = "estimated_velocities_m_ns")

    # Set the default value to NaN
    data["assumed_velocities_m_ns"] = np.nan

    # Use groupby and transform to assign the value of "estimated_velocities_m_ns" for each group
    data["assumed_velocities_m_ns"] = (data.groupby(index_of_nearest_non_nan_col)["estimated_velocities_m_ns"].transform("first"))

    data["calculated_velocities_m_ns"] = np.nan
    for idx, row in data.iterrows():
        lower_limit = row["distance_from_starting_pos_m"] - row[distance_to_nearest_non_nan_col]
        upper_limit = row["distance_from_starting_pos_m"] + row[distance_to_nearest_non_nan_col]
        if lower_limit <= data["distance_from_starting_pos_m"].min():
            lower_limit = data["distance_from_starting_pos_m"].min()
        if upper_limit >= data["distance_from_starting_pos_m"].max():
            upper_limit = data["distance_from_starting_pos_m"].max()
        lower_limit_mask = data["distance_from_starting_pos_m"] >= lower_limit
        upper_limit_mask = data["distance_from_starting_pos_m"] <= upper_limit
        within_window_mask = lower_limit_mask & upper_limit_mask
        data.at[idx, "calculated_velocities_m_ns"] = data.loc[within_window_mask]["assumed_velocities_m_ns"].mean()

    return data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def calculate_frost_table_depths_and_bulk_volumetric_soil_water_content(gdf: gpd.GeoDataFrame, savgol_window_length: int = 251, savgol_poly_order: int = 3) -> gpd.GeoDataFrame:
    """
    Calculates frost table depth and bulk volumetric soil water content using the picking line and the interpolated velocities

    Args:
        gdf - gpd.GeoDataFrame: Input data used for the calculation.
        savgol_window_length - int: Window length of savgol filter. Defaults to 251
        savgol_poly_order - int: Polynomial order of savgol filter. Defaults to 3

    Returns:
        data - gpd.GeoDataFrame: Output data with the calculated values
    """
    # Copy data
    data = gdf.copy()

    # Use calculated velocities to calculate depths
    data["calculated_depths_m"] = (data["refl_line_travel_times_ns"] * data["calculated_velocities_m_ns"]) / 2  # one-way travel time

    #  Convert to bulk_relative_electric_permittivity
    data["bulk_relative_electric_permittivity"] = ((speed_of_light/1e9)/ data["calculated_velocities_m_ns"].replace(0, np.nan))**2

    # Calculate Nielsen and Thomsen 2023 parameterization for volumetric soil water content estimation
    data["volumetric_soil_water_content"] = -4.56*1e-2 + 3.26*1e-2 * data["bulk_relative_electric_permittivity"] - 4.48*1e-4 * data["bulk_relative_electric_permittivity"]**2 + 3.14*1e-6 * data["bulk_relative_electric_permittivity"]**3

    # Smooth data using a Savgol filter
    filtered_values = savgol_filter(data["volumetric_soil_water_content"].fillna(0).astype(float), savgol_window_length, savgol_poly_order)
    data.loc[:, "volumetric_soil_water_content"] = pd.Series(np.asarray(filtered_values, dtype=float), index = data.index)

    # Return data
    return data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def classify_by_thresholds(gdf: gpd.GeoDataFrame, classification_thresholds: dict, class_column: str = "volumetric_soil_moisture_classification", classification_column: str = "volumetric_soil_water_content") -> gpd.GeoDataFrame:
    """
        Classifies the values of a specified column in the transect data based on given thresholds and assigns class labels to a new column.
        The thresholds are stored in a dictionary where the keys are the class labels and the values are lists containing the lower and upper bounds for classification.
        The logic does not check whether the thresholds are overlapping.
        The upper threshold is exclusive, meaning that a value equal to the upper threshold will not be included in that class but in the next one.
        The lower threshold is inclusive, meaning that a value equal to the lower threshold will be included in that class.
    Args:
        gdf - gpd.GeoDataFrame: Geospatial dataframe
        classification_thresholds - dict: Dictionary containing the classification thresholds.
        class_column - str: Name of the column to store the classification results.
        classification_column - str: Name of the column containing the values to classify.

    Returns:
        gdf - gpd.GeoDataFrame: The GeoDataFrame with the classification results added as a new column.
    """
    if class_column in gdf.columns:
        print(f"Warning: Column '{class_column}' already exists in the GeoDataFrame.")

    if classification_column not in gdf.columns:
        raise ValueError(f"Classification column '{classification_column}' not found in GeoDataFrame. Please ensure that the column with the volumetric soil moisture classification values is present in the GeoDataFrame.")

    gdf[class_column] = "unknown"
    for class_name, bounds in classification_thresholds.items():
        if len(bounds) != 2:
            raise ValueError(f"Invalid classification thresholds for class '{class_name}': bounds must be a list of two values [lower_bound, upper_bound].")
        else:
            lower_bound, upper_bound = bounds
        if lower_bound >= upper_bound:
            raise ValueError(f"Invalid classification thresholds for class '{class_name}': lower_bound must be less than upper_bound.")
        if np.isnan(lower_bound) and np.isnan(upper_bound):
            raise ValueError(f"Invalid classification thresholds for class '{class_name}': both lower_bound and upper_bound cannot be NaN.")
        if np.isnan(lower_bound):
            gdf.loc[gdf[classification_column] < upper_bound, class_column] = class_name
        if np.isnan(upper_bound):
            gdf.loc[gdf[classification_column] >= lower_bound, class_column] = class_name
        if not np.isnan(lower_bound) and not np.isnan(upper_bound):
            gdf.loc[(gdf[classification_column] >= lower_bound) & (gdf[classification_column] < upper_bound), class_column] = class_name

    return gdf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def add_surface_topography_to_gpr_trace(gdf: gpd.GeoDataFrame, surface_topography_col: str = "elevation_m_time_delay_ns")-> gpd.GeoDataFrame:
    """
    Adds topography data to the GPR trace by using

    Args:
        gdf - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
        surface_topography_col - str: Column name in transect_data containing surface topography data
    Returns:
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR, GPS, and topography data
    """
    time_delays_ns = gdf[surface_topography_col].values
    samples_to_pad = np.round(time_delays_ns / gdf.iloc[0]["dt_ns"]).astype(int)  # shape (n_traces,)
    max_pad = samples_to_pad.max()
    data = np.array(gdf["trace_values"].tolist()).T  # shape (n_samples, n_traces)
    n_samples, n_traces = data.shape
    new_length = n_samples + max_pad
    data_padded = np.full((new_length, n_traces), np.nan, dtype = data.dtype)
    for i in range(n_traces):
        pad = samples_to_pad[i]
        data_padded[pad:pad + n_samples, i] = data[:, i]
    gdf["trace_values_with_surface_topography"] = data_padded.T.tolist()  # shape (n_traces, n_samples + max_pad)
    return gdf

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
