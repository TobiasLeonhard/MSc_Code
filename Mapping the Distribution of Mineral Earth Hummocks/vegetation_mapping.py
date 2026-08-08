#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
vegetation_mapping.py

This file runs the vegetation classificaiton

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
parent_folder = Path(__file__).resolve().parent
sys.path.append(str(parent_folder))
from config.environment import *
from utility_functions.vegetation_mapping import VegetationClassifier
from utility_functions.combine_tifs import get_combined_raster
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("vegetation_mapping.py started")
    # Define the wanted epsg code
    target_epsg = 3155
    # Define the year for the analysis
    year = 2023
    # Define no data value
    no_data_value = None

    # Define the vegetation files
    raw_data_path = data_folder / "tvc_data" / "mapping"
    veg_1 = raw_data_path / Path("2023-06-02 - Orthomosaic - Siksik").with_suffix(".tif")
    veg_2 = raw_data_path / Path("2023-08-21 - Orthomosaic - Siksik").with_suffix(".tif")
    rgb_rasters = [
        {
            "path":veg_1,
            "resampling": Resampling.bilinear,
            "name": veg_1.stem,
            "bands": [1, 2, 3],
            "overlap_info": {
                "source_bands": [4],
                "nodata_values": [0]
                },
            },
        {
            "path":veg_2,
            "resampling": Resampling.bilinear,
            "name": veg_2.stem,
            "bands": [1, 2, 3],
            "overlap_info": {
                "source_bands": [4],
                "nodata_values": [0]
                },
            },
        ]
    for veg in rgb_rasters:
        if str(year) not in str(veg["path"]):
            raise FileNotFoundError(f"Does not contain year {year}, please check the file path or year.")

    combined_tif_file, sorted_input_rasters = get_combined_raster(
        input_rasters = rgb_rasters,
        target_epsg = target_epsg,
        target_resolution = "lowest",
        nodata_value = no_data_value,
        block_size = 512,
        ensure_equal_resolution = False,
        buffer_size_m = 0.0,
        only_use_true_overlaps = True
        )

    # Build and check the shape files
    vegetation_mapping_folder = manual_input_folder / "vegetation_mapping"
    shape_file_folder = vegetation_mapping_folder / f"{year}"

    # Define output folder for the vegetation mapping results
    output_folder = results_folder/ "vegetation_mapping" / f"{year}"

    pipeline = VegetationClassifier(
        image_path = combined_tif_file,
        polygons_path = shape_file_folder,
        target_epsg_crs = target_epsg,
        output_folder = output_folder,
        test_size = 0.3,
        model_type = "rf",
        dpi = DPI
        )
    pipeline.run_pipeline()

    print("\nvegetation_mapping.py finished.")
    print("# ====================================================================================================================================================== #")
