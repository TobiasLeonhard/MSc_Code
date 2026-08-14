#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
gpr_analysis.py

This script prepares and visualizes GPR reflection pick-line data alongside mapped mineral earth hummocks and aerial imagery.
It overlays hummock maps with radar transects and produces figures for interpretation of hummock-related subsurface structure and moisture conditions.
The resulting plots support comparison between topographic hummock mapping and ground-based geophysical observations.

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-06
Version: 1.0
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent
sys.path.append(str(parent_folder))
from config.environment_hum_prj import *
from config.environment import *
from utility_functions.gpr_handling_hum_prj import plot_hummock_detection
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("gpr_analysis.py started")
    # ----------------------------------------------------------------------------------------------- #
    # Decide on velocities
    used_velocities_m_ns = {
        "no_description": [0.1, "no description"],
        "wet_peat": [0.04, "wet peat"],
        "dry_peat": [0.1, "dry peat"],
        "wet": [0.05, "wet"],
        "moist": [0.08, "moist"],
        "dry": [0.1, "dry"],
        }

    used_velocities_for_plotting_m_ns = {
        "no_description": [0.1, "no description"]
        }

    classification_thresholds = {
        "identified_as_wet": [0.6, 1.0],
        "identified_as_moist": [0.3, 0.6],
        "identified_as_dry": [0.0, 0.3],
        }

    # Decide on rasters
    aerial_map_path_june = data_folder / "tvc_data" / "mapping" / Path("2023-06-02 - Orthomosaic - Siksik").with_suffix(".tif")
    aerial_map_path_august = data_folder / "tvc_data" / "mapping" / Path("2023-08-21 - Orthomosaic - Siksik").with_suffix(".tif")
    hummock_mapping_path = results_folder / "hummock_mapping" / "dtm_mapping" / Path("mapped_hummocks_by_1x1_and_7x7_window_and_p_value_of_0p05_ with_area_between_1p5sqm_and_7p5sqm").with_suffix(".tif")
    path_to_gpr_datasets = results_folder / "gpr_analysis"

    used_rasters_hummock = {
        "Aerial": {
            "path": aerial_map_path_august,
            "resampling": Resampling.bilinear,
            "bands": [1, 2, 3],
            "name": "aerial_map",
            "mapping_style": "RGB",
            "label": None
            },
        "Hummock Mapping": {
            "path": hummock_mapping_path,
            "resampling": Resampling.nearest,
            "bands": [1],
            "name": "hummock_map",
            "mapping_style": "hummock_mapping",
            "label": "Mapped Hummock"
            },
        }

    # Chose pick line folder
    pick_line_folder_path = manual_input_folder / "gpr_analysis" / "Reflection Pick Lines"
    for file in pick_line_folder_path.iterdir():
        if file.is_file():
            plot_hummock_detection(
                file = file,
                used_rasters = used_rasters_hummock,
                dpi = DPI
                )
            gc.collect()

    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\ngpr_analysis.py finished.")
    print("# ====================================================================================================================================================== #")
