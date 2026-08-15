#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
run_all_in_correct_order.py

This files runs all other python files in an order that ensures that all data is produced in time.

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
import subprocess
parent_folder = Path(__file__).resolve().parent

# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("run_all_in_correct_order.py started")

    # List of files to run
    scripts = [
        parent_folder / "Mapping the Distribution of Mineral Earth Hummocks" / Path("run_python_analysis").with_suffix(".py"),
        parent_folder / "Mapping Frost Table Depth and Soil Moisture in an Ice-Wedge Polygon - A Case Study" / Path("run_python_analysis").with_suffix(".py")
        ]

    for script in scripts:
        print(f"Starting {script.parent.name}/{script.name} ...")
        result = subprocess.run([sys.executable, script])

        if result.returncode == 0:
            print(f"{script} finished successfully.")
        else:
            print(f"{script} failed with code {result.returncode}.")

    print("run_all_in_correct_order.py finished.")
    print("# ====================================================================================================================================================== #")
