#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
run_both_chapters.py

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
    print("run_both_chapters.py started")

    # List of files to run
    folders = [
        "Mapping the Distribution of Mineral Earth Hummocks",
        "Mapping Frost Table Depth and Soil Moisture in an Ice Wedge Polygon - A Case Study"
        ]

    for folder in folders:
        script = parent_folder / folder / Path("run_python_analysis").with_suffix(".py")
        print(f"Starting {folder} ...")
        result = subprocess.run([sys.executable, script])

        if result.returncode == 0:
            print(f"{script} finished successfully.")
        else:
            print(f"{script} failed with code {result.returncode}.")

    print("run_both_chapters.py finished.")
    print("# ====================================================================================================================================================== #")
