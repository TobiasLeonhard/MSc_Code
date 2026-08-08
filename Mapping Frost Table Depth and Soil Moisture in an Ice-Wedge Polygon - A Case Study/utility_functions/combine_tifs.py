#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
combine_tifs.py

Utility functions for combining tif files.
This module provides a function to stack multiple rasters into a single multi-band raster, ensuring they are all in the same CRS, resolution, and aligned to the same grid.
It also includes a wrapper function that defines the output path and checks for existing files before creating a new combined raster.'
It is sufficient to call the wrapper function `get_combined_raster` for most use cases, which will handle the output path and file existence checks automatically.

Needed packages: rasterio, numpy, pathlib, contextlib.

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-06
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
def get_resolution(srcs: list, crs: rasterio.crs.CRS, target_resolution: Union[int, float, str], ensure_equal_resolution: bool) -> Tuple[float, float]:
    """
    Helper function to get the resolution of a raster in its native CRS units.
    Args:
        srcs - list: A list of open raster datasets.
        crs - rasterio.crs.CRS: The target coordinate reference system.
        target_resolution - float or str, optional: Target resolution. Defaults to "lowest". If a float is provided, it will be used as the resolution in both x and y directions. If a string is provided, it must be one of "lowest", "highest", or "average", which will calculate the resolution based on the input rasters.
        ensure_equal_resolution - bool: Whether to ensure that the calculated resolution is equal in both x and y directions.
    Returns:
        res_x - float: Resolution in the x-direction (pixel width)
        res_y - float: Resolution in the y-direction (pixel height)
    """
    if isinstance(target_resolution, (int, float)):
        res_x = res_y = float(target_resolution)
    else:
        found_res_x = []
        found_res_y = []
        for src in srcs:
            # Calculate transform and dimensions in one go
            _, width, height = rasterio.warp.calculate_default_transform(src.crs, crs, src.width, src.height, *src.bounds)
            left, bottom, right, top = rasterio.warp.transform_bounds(src.crs, crs, *src.bounds)

            found_res_x.append((right - left) / width)
            found_res_y.append((top - bottom) / height)

        method = target_resolution.lower()
        if method == "lowest":
            res_x, res_y = max(found_res_x), max(found_res_y)
        elif method == "highest":
            res_x, res_y = min(found_res_x), min(found_res_y)
        elif method == "average":
            res_x, res_y = sum(found_res_x)/len(found_res_x), sum(found_res_y)/len(found_res_y)
        else:
            raise ValueError(f"Invalid target_resolution string: {target_resolution}")

    if ensure_equal_resolution:
        # Use the logic requested (e.g., for lowest, take the max of both dimensions)
        val = max(res_x, res_y) if target_resolution == "lowest" else (res_x + res_y) / 2
        res_x = res_y = val

    return res_x, res_y

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def stack_multiple_rasters(input_rasters: list, output_path: Path, target_epsg: int, target_resolution: Union[int, float, str], ensure_equal_resolution: bool, nodata_value:  Union[float, None], block_size: int, buffer_size_m: float, only_use_true_overlaps: bool):
    """
    Stacks multiple rasters into a single multi-band raster, ensuring they are all in the same CRS, resolution, and aligned to the same grid.
    Args:
        input_rasters - list: A list of dictionaries, each must contain:
                             - "path": Path to the raster file
                             - "resampling": Resampling method to use for that raster (e.g., Resampling.nearest, Resampling.mode)
                             - "bands": List of band indices to extract from that raster (e.g., [1] for the first band, [1, 2] for the first two bands, etc.)
                             - "overlap_info": A dictionary containing information about the overlap for that raster, with keys:
                                 - "source_bands": List of band indices in the source raster that contain the overlap
                                 - "nodata_values": List of NoData values corresponding to the source bands that indicate non-overlap areas
        output_path - Path: Path to save the output stacked raster
        target_epsg - int, optional: Target EPSG code. Defaults to 3155.
        target_resolution - float or str, optional: Target resolution. Defaults to None = "lowest". If a float is provided, it will be used as the resolution in both x and y directions. If a string is provided, it must be one of "lowest", "highest", or "average", which will calculate the resolution based on the input rasters.
        nodata_value - float, optional: NoData value. Defaults to None.
        block_size - int, optional: Block size for the output raster. Defaults to 512.
        buffer_size_m - float, optional: Buffer size in meters for the output raster. Defaults to 0.0.
        only_use_true_overlaps - bool, optional: Whether to only use true overlaps when combining rasters. True overlap means area that has values that are not NoData. Defaults to False.
    Raises:
        ValueError: If the provided rasters do not all intersect in the target CRS.
    """
    # Define the target CRS
    aimed_crs = rasterio.crs.CRS.from_epsg(target_epsg)
    total_output_bands = 0
    # Check input rasters - ensure they have required keys and files exist and resampling is valid
    for raster in input_rasters:
        # Basic validation of input raster configurations
        if "path" not in raster or "resampling" not in raster or "bands" not in raster:
            raise ValueError("Each input raster configuration must contain 'path', 'resampling', and 'bands' keys.")
        # Check if the raster file exists
        if not raster["path"].exists():
            raise FileNotFoundError(f"Raster file not found: {raster['path']}")
        # Check if resampling method is valid
        if not isinstance(raster["resampling"], rasterio.enums.Resampling):
            raise ValueError(f"Resampling method for raster {raster['path']} must be an instance of rasterio.enums.Resampling.")
        if not isinstance(raster["bands"], list) or not all(isinstance(b, int) for b in raster["bands"]):
            raise ValueError(f"Band specification for raster {raster['path']} must be a list of integers.")
        total_output_bands += len(raster["bands"])

    if total_output_bands == 0:
        raise ValueError("At least one band must be specified across the input rasters.")

    if only_use_true_overlaps == True:
        for raster in input_rasters:
            if "overlap_info" not in raster:
                only_use_true_overlaps = False
                print(f"⚠️ Warning: No overlap_info found for raster {raster['path']}. Cannot apply true overlap filtering. Using all requested bands for this source.")
                continue

    # Use ExitStack to manage multiple open files and contexts
    with ExitStack() as stack:
        srcs = [stack.enter_context(rasterio.open(r["path"])) for r in input_rasters]

        # 1. Calculate Bounds
        left_list, bottom_list, right_list, top_list = [], [], [], []
        for src in srcs:
            l, b, r, t = rasterio.warp.transform_bounds(src.crs, aimed_crs, *src.bounds)
            if not aimed_crs.is_projected:
                buff_h = buffer_size_m / 111320
                buff_w = buffer_size_m / (111320 * np.cos(np.radians((t + b) / 2)))
            else:
                buff_h = buff_w = buffer_size_m
            left_list.append(l - buff_w); bottom_list.append(b - buff_h)
            right_list.append(r + buff_w); top_list.append(t + buff_h)

        bbox_left, bbox_bottom = max(left_list), max(bottom_list)
        bbox_right, bbox_top = min(right_list), min(top_list)

        if bbox_left >= bbox_right or bbox_bottom >= bbox_top:
            raise ValueError("The provided rasters do not intersect.")

        # 2. Resolution & Transform
        res_x, res_y = get_resolution(
            srcs = srcs,
            crs = aimed_crs,
            target_resolution = target_resolution,
            ensure_equal_resolution = ensure_equal_resolution
            )
        dst_width = int(np.ceil((bbox_right - bbox_left) / res_x))
        dst_height = int(np.ceil((bbox_top - bbox_bottom) / res_y))
        dst_transform = rasterio.transform.from_origin(bbox_left, bbox_top, res_x, res_y)

        # 3. Determine Output Dtype and NoData
        highest_dtype = np.result_type(*[src.dtypes[0] for src in srcs])

        # Ensure out_nodata is compatible with the dtype
        if nodata_value is not None:
            out_nodata = nodata_value
        elif srcs[0].nodata is not None:
            out_nodata = srcs[0].nodata
        else:
            # Fallback based on type
            if highest_dtype == np.uint8:
                out_nodata = 0
            elif np.issubdtype(highest_dtype, np.integer):
                out_nodata = -9999
            elif np.issubdtype(highest_dtype, np.floating):
                out_nodata = np.nan
            else:
                raise ValueError(f"Unsupported data type for NoData value: {highest_dtype}")

        out_profile = {
            "driver": "GTiff",
            "bigtiff": "YES",
            "dtype": highest_dtype,
            "height": dst_height,
            "width": dst_width,
            "count": sum(len(r["bands"]) for r in input_rasters),
            "crs": aimed_crs,
            "transform": dst_transform,
            "nodata": out_nodata,
            "tiled": True,
            "blockxsize": block_size,
            "blockysize": block_size,
            "compress": "lzw",
            "predictor": 2 if np.issubdtype(highest_dtype, np.integer) else 3,
            "num_threads": "all_cpus"
            }

        dst = stack.enter_context(rasterio.open(output_path, "w", **out_profile))
        dst.colorinterp = [ColorInterp.undefined] * out_profile["count"]

        # 4. WarpedVRTs
        vrts = []
        for i, src in enumerate(srcs):
            vrt = stack.enter_context(
                WarpedVRT(
                    src, crs = aimed_crs, transform = dst_transform,
                    width = dst_width, height = dst_height,
                    resampling = input_rasters[i]["resampling"],
                    src_nodata = src.nodata, nodata = out_nodata,
                    warp_extras = {"NUM_THREADS": "ALL_CPUS"}
                )
            )
            vrts.append(vrt)

        # 5. The Window Loop
        total_bands = out_profile["count"]

        for _, window in dst.block_windows():
            # Initialize a blank window filled with NoData
            # This ensures that even if we skip data, the block is written correctly.
            window_output = np.full((total_bands, window.height, window.width),
                                   out_nodata, dtype = highest_dtype)

            # Create the True Overlap Mask
            valid_mask = np.ones((window.height, window.width), dtype = bool)

            # Step A: Pre-calculate the mask if requested
            if only_use_true_overlaps:
                for i, vrt in enumerate(vrts):
                    info = input_rasters[i].get("overlap_info")
                    if info:
                        for idx, b_idx in enumerate(info["source_bands"]):
                            # Read specifically for the mask
                            m_data = vrt.read(b_idx, window=window)
                            m_nodata = info["nodata_values"][idx]

                            # 1. Handle Empty List or None (Everything is valid)
                            if m_nodata is None or (isinstance(m_nodata, (list, tuple, np.ndarray)) and len(m_nodata) == 0):
                                band_valid = np.ones(m_data.shape, dtype=bool)

                            # 2. Handle List/Array of multiple values
                            elif isinstance(m_nodata, (list, tuple, np.ndarray)):
                                band_valid = ~np.isin(m_data, m_nodata)
                                # Manually check for NaNs if they are in the list
                                if any(np.isnan(x) for x in m_nodata if isinstance(x, (float, np.floating))):
                                    band_valid &= ~np.isnan(m_data)

                            # 3. Handle Single NaN
                            elif np.isnan(m_nodata):
                                band_valid = ~np.isnan(m_data)

                            # 4. Handle Single Numeric Value
                            else:
                                band_valid = (m_data != m_nodata)

                            # Combine with the master mask
                            valid_mask &= band_valid


            # Step B: Only read and fill data if there's anything valid in the mask
            if not only_use_true_overlaps or np.any(valid_mask):
                current_band_idx = 0
                for i, vrt in enumerate(vrts):
                    requested_bands = input_rasters[i]["bands"]
                    num_bands = len(requested_bands)

                    # Read the actual data
                    data = vrt.read(requested_bands, window = window).astype(highest_dtype)

                    # If using overlaps, apply the mask
                    if only_use_true_overlaps:
                        # For every band in this source, set invalid pixels to nodata
                        for b in range(num_bands):
                            data[b, ~valid_mask] = out_nodata

                    # Place data into our pre-initialized window_output
                    window_output[current_band_idx : current_band_idx + num_bands, :, :] = data
                    current_band_idx += num_bands

            # Step C: ALWAYS write the window to the file
            dst.write(window_output, window = window)

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
def get_combined_raster(input_rasters: Union[list, dict], target_epsg: int = 3155, target_resolution: Union[int, float, str] = "lowest", nodata_value: Union[float, None] = None, block_size: int = 512, ensure_equal_resolution: bool = False, buffer_size_m: float = 0.0, only_use_true_overlaps: bool = False) -> Tuple[Path, list]:
    """
    A wrapper function that calls stack_multiple_rasters and creates a combined raster.
    This function defines the output path, checks whether the output file already exists, and then calls the stacking function, if needed.
    Args:
        project_path - Path: The project path. This is used to construct the output path for the combined raster.
        input_rasters - list/dict: A list/dict of dictionaries, each containing:
                             - "path": Path to the raster file
                             - "resampling": Resampling method to use for that raster (e.g., Resampling.nearest, Resampling.mode)
                             - "bands": List of band indices to extract from that raster (e.g., [1] for the first band, [1, 2] for the first two bands, etc.)
                             Example:
                             example_rasters = [
                                {"path": file_path_1, "resampling": Resampling.nearest, "bands": [1]},
                                {"path": file_path_2, "resampling": Resampling.mode, "bands": [1]},
                                ]
        target_epsg - int, optional: Target EPSG code. Defaults to 3155.
        target_resolution - Union[float, str], optional: Target resolution. Defaults to None = "lowest". If a float is provided, it will be used as the resolution in both x and y directions. If a string is provided, it must be one of "lowest", "highest", or "average", which will calculate the resolution based on the input rasters.
        nodata_value - float, optional: NoData value. Defaults to None.
        block_size - int, optional: Block size for the output raster. Defaults to 512.
        ensure_equal_resolution - bool, optional: Whether to ensure all input rasters have the same resolution. Defaults to False.
        buffer_size_m - float, optional: Buffer size in meters for the output raster. Defaults to 0.0.
        only_use_true_overlaps - bool, optional: Whether to only use true overlaps when combining rasters. True overlap means area that has values that are not NoData. Defaults to False.
    Returns:
        output_path - Path: Path to save the output stacked raster
        sorted_input_rasters - list: The list of input rasters (sorted by path stem for consistent naming)
    """
    # Create output path folder if it doesn't exist
    output_path = results_folder / "created_tifs"
    output_path.mkdir(parents = True, exist_ok = True)

    # Sort input rasters by their path stem to ensure consistent output naming regardless of input order
    if isinstance(input_rasters, dict):
        input_rasters = list(input_rasters.values())
    elif not isinstance(input_rasters, list):
        raise ValueError("input_rasters must be a list or a dictionary.")
    sorted_input_rasters = sorted(input_rasters, key = lambda x: int(x["path"].stem) if x["path"].stem.isdigit() else x["path"].stem)

    # -------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # Create a descriptive output filename based on the input rasters, their bands, resampling methods, target resolution, and nodata value
    output_stem = ""

    for raster_config in sorted_input_rasters:
        # Add the stem of the raster path to the output filename
        output_stem += raster_config["path"].stem + "_"
        output_stem += "bands_"
        # Depending on the overlap settings, we either include all bands in the filename or only the true overlap bands
        for b in raster_config["bands"]:
            output_stem += str(b) + "_"

        # Add the resampling method to the output filename
        output_stem += raster_config["resampling"].name + " - "

    # Add the target EPSG code to the output filename
    output_stem += f"epsg{target_epsg}_"

    # Add the resolution to the output filename
    if isinstance(target_resolution, (str)):
        target_resolution_str = target_resolution.lower()
    elif isinstance(target_resolution, (int, float)):
        target_resolution_str = str(target_resolution).replace(".", "p") + "_m" # Replace dot with 'p' for filename compatibility
    else:
        raise ValueError(f"Invalid target_resolution type: {type(target_resolution)}. Must be a string or a number.")
    output_stem += f"res_{target_resolution_str}_"

    # Add nodata information to the output filename
    if nodata_value is not None:
        nodata_str = f"nodata_{nodata_value}_"
    else:
        nodata_str = "nodata_auto_"
    output_stem += nodata_str

    # Add buffer size information to the output filename
    buffer_size_m_str = str(buffer_size_m).replace(".", "p") # Replace dot with 'p' for filename compatibility
    output_stem += f"buffer_{buffer_size_m_str}m"

    # Finalize output path with .tif extension
    output_path = output_path / Path(output_stem).with_suffix(".tif")

    # -------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # Check if output file already exists
    if output_path.exists():
        print(f"Output file already exists at: {output_path}. Skipping processing and returning existing file.")
    else:
        print(f"Output file does not exist. Creating new file at: {output_path}")
        # Create the file by calling the stack_multiple_rasters function
        stack_multiple_rasters(
            input_rasters = sorted_input_rasters,
            output_path = output_path,
            target_epsg = target_epsg,
            target_resolution = target_resolution,
            ensure_equal_resolution = ensure_equal_resolution,
            nodata_value = nodata_value,
            block_size = block_size,
            buffer_size_m = buffer_size_m,
            only_use_true_overlaps = only_use_true_overlaps
            )

        print(f"Success! Saved to: {output_path}")
    # Return the output path and the sorted input rasters for reference
    return output_path, sorted_input_rasters

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
