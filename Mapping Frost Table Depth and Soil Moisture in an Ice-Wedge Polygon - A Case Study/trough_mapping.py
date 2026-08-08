#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
trough_mapping.py

This file handles all hummock mapping processes.
It creates different hummock maps using the DTM from the KBM LIDAR campaing 2024

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
parent_folder = Path(__file__).resolve().parent
sys.path.append(str(parent_folder))
from config.environment import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("trough_mapping.py started")

    # --- 1. Setup Paths ---
    dtm_file = data_folder / "tvc_data" / "mapping" / Path("2024 - LIDAR - DTM - Siksik").with_suffix(".tif")
    output_folder = results_folder / "trough_mapping"
    output_folder.mkdir(parents=True, exist_ok=True)
    iwp_precise_file = manual_input_folder / Path("outline_of_ice_wedge_polygon_study_site").with_suffix(".gpkg")
    output_file = output_folder / Path("mapped_troughs").with_suffix(".gpkg")

    # --- 2. Calculate Diff From Mean Elevation ---
    filter_length = 11
    diff_file = output_folder / Path(f"{dtm_file.stem} - diff_from_mean_elev - {filter_length}-{filter_length}").with_suffix(".tif")

    if not diff_file.exists():
        wbt.diff_from_mean_elev(
            str(dtm_file),
            str(diff_file),
            filterx=filter_length,
            filtery=filter_length
        )

    # --- 3. Load Study Area and Clip Raster ---
    iwp_area = gpd.read_file(iwp_precise_file)

    with rasterio.open(diff_file) as src:
        # Ensure CRS match for masking
        if iwp_area.crs != src.crs:
            iwp_area = iwp_area.to_crs(src.crs)

        # Mask the raster to the shapefile
        # crop=True keeps the array small; all_touched=True ensures edge pixels are kept
        out_image, out_transform = mask(src, iwp_area.geometry, crop=True)
        out_meta = src.meta.copy()
        nodata = src.nodata if src.nodata is not None else -9999.0
        resolution = src.res[0]

    # --- 4. Thresholding and Vectorization ---
    # Instead of Points, we create Polygons from pixel clusters
    band1 = out_image[0]
    threshold = -0.03
    # Create a binary mask (1 for trough, 0 for not)
    trough_mask = (band1 <= threshold) & (band1 != nodata)
    trough_mask = trough_mask.astype("int16")

    # Convert the "1" pixels into Polygon geometries
    results = (
        {"properties": {"Is_Trough": 1}, "geometry": s}
        for i, (s, v)
        in enumerate(shapes(trough_mask, mask = (trough_mask == 1), transform = out_transform))
    )

    # Create GeoDataFrame from polygons
    trough_polygons = gpd.GeoDataFrame.from_features(list(results), crs = src.crs)

    if trough_polygons.empty:
        print("No troughs found with the current threshold.")
        sys.exit()

    # --- 5. Project, Filter by Area, and Clean Up ---
    # Move to target CRS
    trough_polygons = trough_polygons.to_crs("EPSG:3155")
    iwp_area_3155 = iwp_area.to_crs("EPSG:3155")

    # Filter by area (now works because these are Polygons)
    min_area = 17
    trough_polygons = trough_polygons[trough_polygons.geometry.area >= min_area]

    # IMPORTANT: Clip to the original shapefile boundary
    # This removes any pixels that "leaked" outside the SHP boundary during the process
    trough_polygons = gpd.clip(trough_polygons, iwp_area_3155)

    # --- 6. Save Vector Output ---
    trough_polygons.to_file(output_file, driver="GPKG")

    # --- 7. Save Raster Output ---
    # We use the cleaned GeoDataFrame to create a raster
    # We use the iwp_area_3155 as a "template" to define the grid extent
    geo_grid = make_geocube(
        vector_data = trough_polygons,
        measurements = ["Is_Trough"],
        resolution = (-resolution, resolution),
        fill = 0 # Non-trough areas are 0
        )

    # Final clip of the raster to ensure no pixels exist outside the SHP boundary
    geo_grid["Is_Trough"] = geo_grid["Is_Trough"].rio.write_nodata(0)
    final_raster = geo_grid["Is_Trough"].rio.clip(
            iwp_area_3155.geometry,
            iwp_area_3155.crs
            ).astype("uint8")
    final_raster.rio.to_raster(output_file.with_suffix(".tif"), dtype = "uint8")

    print(f"Files saved to: {output_file}")
    print("trough_mapping.py finished.")
    print("# ====================================================================================================================================================== #")
