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

This file organizes the GPR analysis

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
from utility_functions.gpr_handling import plot_iwp_transect_wise, plot_whole_iwp_side
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
    trough_mapping = results_folder / "trough_mapping" / Path("mapped_troughs").with_suffix(".tif")
    path_to_gpr_datasets = results_folder / "gpr_analysis"

    used_rasters_iwp = {
            "Aerial": {
                "path": aerial_map_path_june,
                "resampling": Resampling.bilinear,
                "bands": [1, 2, 3],
                "name": "aerial_map",
                "mapping_style": "RGB",
                "label": None
                },
            "Trough Mapping": {
                "path": trough_mapping,
                "resampling": Resampling.nearest,
                "bands": [1],
                "name": "trough_map",
                "mapping_style": "trough_mapping",
                "label": "Mapped Trough"
                },
        }

    # Chose pick line folder
    pick_line_folder_path = manual_input_folder / "gpr_analysis" / "Reflection Pick Lines"
    for file in pick_line_folder_path.iterdir():
        if file.is_file():
            plot_iwp_transect_wise(
                file = file,
                used_rasters = used_rasters_iwp,
                used_velocities_m_ns = used_velocities_m_ns,
                used_velocities_for_plotting_m_ns = used_velocities_for_plotting_m_ns,
                classification_thresholds = classification_thresholds,
                dpi = DPI
                )
            gc.collect()

    plot_whole_iwp_side(
        path_to_gpr_datasets = path_to_gpr_datasets,
        used_rasters = used_rasters_iwp,
        dpi = 2 * DPI
        )
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\ngpr_analysis.py finished.")
    print("# ====================================================================================================================================================== #")
