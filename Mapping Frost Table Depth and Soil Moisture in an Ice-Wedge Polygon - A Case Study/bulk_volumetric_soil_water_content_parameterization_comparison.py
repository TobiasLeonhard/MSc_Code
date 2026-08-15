#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
bulk_volumetric_soil_water_content_parameterization_comparison.py

Description:
This script compares two empirical parameterizations for converting relative electric permittivity to volumetric soil water content.
It plots the Topp et al. (1980) and Nielsen & Thomsen (2023) polynomials to visualize differences in soil moisture estimation from GPR-derived dielectric properties, supporting methodological assessment of GPR-based hydrological measurements.

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
    print("bulk_volumetric_soil_water_content_parameterization_comparison.py started")
    save_path = results_folder / "gpr_analysis" / Path("parameterization_comparison").with_suffix(".png")
    save_path.parent.mkdir(exist_ok = True)
    relative_electric_permittivity = np.linspace(0, 60, 1000)
    # Calculate Topp et al. 1980 parameterization for volumetric soil water content estimation
    topp_et_all = -5.3*1e-2 + 2.92*1e-2 * relative_electric_permittivity - 5.5*1e-4 * relative_electric_permittivity**2 + 4.3*1e-6 * relative_electric_permittivity**3
    # Calculate Nielsen and Thomsen 2023 parameterization for volumetric soil water content estimation
    nielsen_and_thomsen = -4.56*1e-2 + 3.26*1e-2 * relative_electric_permittivity - 4.48*1e-4 * relative_electric_permittivity**2 + 3.14*1e-6 * relative_electric_permittivity**3

    plt.figure(figsize=(8, 5))
    plt.plot(
        relative_electric_permittivity,
        topp_et_all,
        label = "Topp et al. 1980",
        color = "orange",
        linestyle = "-."
        )
    plt.plot(
        relative_electric_permittivity,
        nielsen_and_thomsen,
        label = "Nielsen & Thomsen 2023",
        color = custom_colors["wlu_purple"]
        )
    plt.xlabel("Relative Electric Permittivity (-)")
    plt.ylabel("Volumetric Soil Water Content (m$^3$ m$^{-3}$)")
    plt.title("Comparison of Soil Water Content Parameterizations")
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path, dpi = DPI)

    print("\nbulk_volumetric_soil_water_content_parameterization_comparison.py finished.")
    print("# ====================================================================================================================================================== #")
