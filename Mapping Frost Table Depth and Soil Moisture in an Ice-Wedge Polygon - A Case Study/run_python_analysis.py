#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
run_python_analysis.py

Description:
This script orchestrates the full analytical workflow for the ice-wedge polygon study by sequentially executing soil moisture parameterization comparison, climate normalization, trough mapping, and GPR analysis scripts.
It ensures that all intermediate and derived datasets are generated in a consistent order for reproducible interpretation of permafrost thermal and hydrological conditions.

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-14
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
    print("run_python_analysis.py started")

    # List of files to run
    scripts = [
        # "prepare_analysis_iwp_prj",
        "bulk_volumetric_soil_water_content_parameterization_comparison", "climate_normals",
        "trough_mapping", "gpr_analysis"
        ]

    for name in scripts:
        script = coding_folder / Path(name).with_suffix(".py")
        print(f"Starting {name}.py...")
        result = subprocess.run([sys.executable, script])

        if result.returncode == 0:
            print(f"{script} finished successfully.")
        else:
            print(f"{script} failed with code {result.returncode}.")

    print("run_python_analysis.py finished.")
    print("# ====================================================================================================================================================== #")
