#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
gpr_handling_hum_prj.py

This file handles the GPR processing for easier reading.

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
from config.environment_hum_prj import *
from config.environment import *
from utility_functions.gpr_processing_hum_prj import load_data_for_hummock_detection
from utility_functions.gpr_plotting_hum_prj import plot_hummock_detection_transect
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_hummock_detection(file: Path, used_rasters: dict, dpi: int) -> None:
    """
    Handles the plotting of the transect wise results for the hummock identification
    Args:
        file - Path: Path of the used file.
        used_rasters - dict: Dictionary containing the TIF files.
        used_velocities_m_ns - dict: Dictionary of lib. ground velocities
        used_velocities_for_plotting_m_ns - dict: Dictionary for velocities for plotting.
        classification_thresholds - dict: Dictionary for classifying tresholds for wet, dry, and moist areas
        dpi - int: DPI values for figures
    """
    if "1GHz" in file.stem or "1GHZ" in file.stem:
        return None
    if file.stem.startswith("W"):
        return None
    # skip all non-hummock transects for now
    if "_H_" not in file.stem:
        return None
    sgy_file = manual_input_folder / "gpr_analysis" / "Radargrams" / Path(file.stem.split("_H_")[0]).with_suffix(".SGY")
    pck_file = file.with_suffix(".PCK")
    transect_data, image_info = load_data_for_hummock_detection(
        sgy_file = sgy_file,
        pck_file = pck_file,
        tif_files = used_rasters,
        epsg_code = 3155,
        cut_half_width_m = 10
        )
    plot_hummock_detection_transect(
        transect_data = transect_data,
        image_data = image_info,
        pck_file = pck_file,
        cut_half_width_m = 10,
        fig_width_cm = 30,
        height_unit_cm = 7.5,
        dpi = dpi
        )

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
