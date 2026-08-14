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

This script runs the full analytical workflow for the mineral earth hummock mapping project by
sequentially executing the climate, uncertainty, vegetation, topographic mapping, vegetation comparison, and GPR analysis scripts.
It ensures that all intermediate and derived datasets are generated in a consistent order for reproducible analysis and interpretation.

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
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("run_python_analysis.py started")

    # List of files to run
    scripts = [
        "climate_normals", "error_propagation_calculations",
        "vegetation_mapping", "hummock_mapping", "compare_hummock_mapping_with_vegetation_classification",
        "gpr_analysis"
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
