#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
gpr_handling_iwp_prj.py

Description:
This module orchestrates GPR transect processing and multi-scale visualization for ice-wedge polygon analysis.
It loads radargrams with velocity-based moisture classification, generates transect-scale and site-wide figures with overlaid spatial data, extracts frost table depth and soil water content, and performs non-parametric statistical tests (Kruskal-Wallis, Dunn's post-hoc, Mann-Whitney U) to compare conditions across polygon zones.
Results are compiled into publication-ready tables supporting permafrost hydrothermal interpretation.

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-14
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment_iwp_prj import *
from config.environment import *
from utility_functions.python_to_latex import export_to_latex
from utility_functions.gpr_processing_iwp_prj import load_data_for_iwp_transect, load_iwp_gdfs
from utility_functions.gpr_plotting_iwp_prj import plot_transect_wise_in_IWP_setting, plot_subtransect_of_IWP_transect, plot_whole_iwp_figure
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_iwp_transect_wise(file: Path, used_rasters: dict, used_velocities_m_ns: dict, used_velocities_for_plotting_m_ns: dict, classification_thresholds: dict, dpi: int) -> None:
    """
    Handles the plotting of the transect wise results for the IWP study site.
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
    if "_H_" in file.stem:
        return None


    # Predefine estimated features
    assumed_features = None

    subtransects = [[]]
    # Define empty drop_frozen_table_measurements
    drop_frozen_table_measurements = np.array([])


    if file.stem.startswith("W"):
        return None  # skip all winter transects for now
    if not "IWP" in file.stem:
        return None

    if "IWP-1-2" in file.stem:
        assumed_features = {
            "wet": np.array([
                [20, 30],
                [90, 100],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [],
                ])
            }
        subtransects = [
            [],
            ]
        drop_frozen_table_measurements = np.array([
            [0, 5]
            ])
    elif "IWP-2-3" in file.stem:
        assumed_features = {
            "wet": np.array([
                [60, 70],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [],
                ])
            }
        drop_frozen_table_measurements = np.array([
            [60, 70],
            ])
        subtransects = [
            [],
            ]
    elif "IWP-3-4" in file.stem:
        assumed_features = {
            "wet": np.array([
                [20, 30],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [],
                ])
            }
        subtransects = [
            [],
            [22, 25],
            ]
    elif "IWP-4-5" in file.stem:
        assumed_features = {
            "wet": np.array([
                [20, 30],
                [85, 90],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [70, 80],
                [81, 90],
                ])
            }
        drop_frozen_table_measurements = np.array([
            [80, 95],
            ])
        subtransects = [
            [],
            ]
    elif "IWP-5-6" in file.stem:
        assumed_features = {
            "wet": np.array([
                [40, 60],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [],
                ])
            }
        subtransects = [
            [],
            ]
    elif "IWP-6-7" in file.stem:
        assumed_features = {
            "wet": np.array([
                [140, 150],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [],
                ])
            }
        drop_frozen_table_measurements = np.array([
            [50, 55],
            [160, 170],
            ])
        subtransects = [
            [],
            ]
    elif "IWP-7-8" in file.stem:
        assumed_features = {
            "wet": np.array([
                [30, 40],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [],
                ])
            }
        drop_frozen_table_measurements = np.array([
            [69, 79],
            ])
        subtransects = [
            [],
            [30, 34],
            ]
    elif "IWP-8-9" in file.stem:
        assumed_features = {
            "wet": np.array([
                [30, 40],
                [60, 70],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [],
                ])
            }
        drop_frozen_table_measurements = np.array([
            [60, 70],
            ])
        subtransects = [
            [],
            ]
    elif "IWP-9-1" in file.stem:
        assumed_features = {
            "wet": np.array([
                [20, 30],
                [45, 55],
                ]),
            "moist": np.array([
                [],
                ]),
            "dry": np.array([
                [10, 20],
                ])
            }
        drop_frozen_table_measurements = np.array([
            [10, 20],
            [45, 55],
            ])
        subtransects = [
            [],
            ]
    else:
        return None
    print("Generating figure for:", file.stem)

    sgy_file = manual_input_folder / "gpr_analysis" / "Radargrams" / Path(file.stem).with_suffix(".SGY")
    pck_file = file.with_suffix(".PCK")
    transect_data, image_info = load_data_for_iwp_transect(
        sgy_file = sgy_file,
        pck_file = pck_file,
        tif_files = used_rasters,
        used_velocities_m_ns = used_velocities_m_ns,
        classification_thresholds = classification_thresholds,
        epsg_code = 3155,
        cut_half_width_m = 10.0,
        drop_frozen_table_measurements = drop_frozen_table_measurements,
        assumed_features = assumed_features
        )

    plot_transect_wise_in_IWP_setting(
        transect_data = transect_data,
        image_data = image_info,
        used_velocities_m_ns = used_velocities_for_plotting_m_ns,
        pck_file = pck_file,
        cut_half_width_m = 10.0,
        fig_width_cm = 30,
        height_unit_cm = 7.5,
        dpi = dpi
        )
    for _, subtransect in enumerate(subtransects):
        if subtransect == []:
            continue
        elif len(subtransect) == 1 or len(subtransect) > 2:
            raise NotImplementedError("The option to plot subtransects is not implemented yet. Please give a start and a end point.")
        elif len(subtransect) == 2:
            start_point = subtransect[0]
            end_point = subtransect[1]
            plot_subtransect_of_IWP_transect(
                start_point= start_point,
                end_point= end_point,
                transect_data = transect_data,
                image_data = image_info,
                pck_file = pck_file,
                cut_half_width_m = 10.0,
                fig_width_cm = 30,
                height_unit_cm = 7.5,
                dpi = dpi
                )
        else:
            raise ValueError("Invalid value for subtransect. Expected an empty list for the full transect, or a list with two values indicating the start and end point of the subtransect to be plotted.")

    return None

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_whole_iwp_side(path_to_gpr_datasets: Path, used_rasters: dict, dpi: int) -> None:
    """
    Plots the IWP study site as a whole figure

    Args:
        path_to_gpr_datasets - Path: Path to folder containing the gpr datasets.
        sed_rasters - dict: Dictionary containing the TIF files.
        dpi - int: dpi for plotting.
    """
    gdf = load_iwp_gdfs(
        path_to_gdfs = path_to_gpr_datasets
        )
    save_folder = results_folder / "gpr_analysis"
    save_folder.mkdir(parents=True, exist_ok=True)
    runs = [
        {
            "save_path": save_folder / "Whole IWP Figure for Bulk Volumetric Water Content.png",
            "plot_overlay":  {
                "volumetric_soil_water_content": [
                    "Bulk Volumetric Soil Water Content (m³m⁻³)",
                    "viridis_r"
                        ]
                },
            "title": "All GPR transects at the Ice-Wedge Polygon Site ",
            "buffer": 5,
            "subtransect_rectangles": [
                {
                "easting_min": 561285.0,
                "easting_max": 561295.0,
                "northing_min": 7626825.0,
                "northing_max": 7626845.0,
                "x_text": 561278.0,
                "y_text": 7626847.0,
                "edgecolor": "red",
                "linewidth": 2,
                "linestyle": "--",
                "text_color": "black",
                "text_bg": "white"
                },
                {
                "easting_min": 561315.0,
                "easting_max": 561330.0,
                "northing_min": 7626835.0,
                "northing_max": 7626828.0,
                "x_text": 561315.0,
                "y_text": 7626845.0,
                "edgecolor": "blue",
                "linewidth": 2.5,
                "linestyle": "-.",
                "text_color": "black",
                "text_bg": "white"
                }
                ]
            },
        {
            "save_path": save_folder / "Whole IWP Figure for Frost Table Depth.png",
            "plot_overlay":  {
                "calculated_depths_m": [
                    "Frost Table Depth (m)",
                    "plasma_r"
                        ]
                },
            "title": "All GPR transects at the Ice-Wedge Polygon Site",
            "buffer": 5,
            "subtransect_rectangles": []
            }
        ]
    results = []
    gdfs_only_center = []
    gdfs_everything_else = []
    for run in runs:
        result, gdf_only_center, gdf_everything_else = plot_whole_iwp_figure(
            gdf = gdf,
            input_rasters = used_rasters,
            save_path = run["save_path"],
            plot_overlay = run["plot_overlay"],
            title = run["title"],
            subtransect_rectangles= run["subtransect_rectangles"],
            dpi = dpi,
            buffer = run["buffer"],
            wanted_epsg_crs = 3155
            )
        results.append(result)
        gdfs_only_center.append(gdf_only_center)
        gdfs_everything_else.append(gdf_everything_else)

    results = pd.merge(
        pd.DataFrame(results[0]),
        pd.DataFrame(results[1]),
        on = ["Description", "Description"],
        how = "left"
        )
    results["Bulk Volumetric Soil \\\\ Water Content (\\unit{\\cubic\\meter\\per\\cubic\\meter})"] = "$" + results["Mean Bulk Volumetric Soil Water Content (m³m⁻³)"].map("{:.2f}".format) +" \\pm " + results["Std Bulk Volumetric Soil Water Content (m³m⁻³)"].map("{:.2f}".format) + "$"
    results["Frost Table \\\\ Depth (\\unit{\\meter})"] = "$" + results["Mean Frost Table Depth (m)"].map("{:.2f}".format) + " \\pm " + results["Std Frost Table Depth (m)"].map("{:.2f}".format) + "$"
    results = results.loc[:, ["Description", "Bulk Volumetric Soil \\\\ Water Content (\\unit{\\cubic\\meter\\per\\cubic\\meter})", "Frost Table \\\\ Depth (\\unit{\\meter})"]]

    # Calculate Kruskal-Wallis + Dunn's Post-Hoc
    # 1. Group data
    data_vswc = [
        gdfs_only_center[0].loc[(gdfs_only_center[0]["iwp_mapping_values"] == 1), "volumetric_soil_water_content"],
        gdfs_only_center[0].loc[(gdfs_only_center[0]["iwp_mapping_values"] == 0), "volumetric_soil_water_content"],
        gdfs_everything_else[0].loc[(gdfs_everything_else[0]["iwp_mapping_values"] == 1), "volumetric_soil_water_content"],
        gdfs_everything_else[0].loc[(gdfs_everything_else[0]["iwp_mapping_values"] == 0), "volumetric_soil_water_content"]
        ]

    data_ftd = [
        gdfs_only_center[1].loc[(gdfs_only_center[1]["iwp_mapping_values"] == 1), "calculated_depths_m"],
        gdfs_only_center[1].loc[(gdfs_only_center[1]["iwp_mapping_values"] == 0), "calculated_depths_m"],
        gdfs_everything_else[1].loc[(gdfs_everything_else[1]["iwp_mapping_values"] == 1), "calculated_depths_m"],
        gdfs_everything_else[1].loc[(gdfs_everything_else[1]["iwp_mapping_values"] == 0), "calculated_depths_m"]
        ]
    # 2. Perform Kruskal-Wallis
    _, kw_p_vswc = scipy.stats.kruskal(*data_vswc)
    _, kw_p_ftd = scipy.stats.kruskal(*data_ftd)

    print(f"Kruskal-Wallis P-value for volumetric soil water content: {kw_p_vswc}")
    print(f"Kruskal-Wallis P-value for frost table depth: {kw_p_ftd}")

    # 3. Perform Dunn's Post-Hoc if p value < 0.05
    if kw_p_vswc < 0.05:
        posthoc_vswc = sp.posthoc_dunn(data_vswc, p_adjust = "holm")
        print(posthoc_vswc)
    else:
        print("No significant differences found between groups for volumetric soil water content.")

    if kw_p_ftd < 0.05:
        posthoc_ftd = sp.posthoc_dunn(data_ftd, p_adjust = "holm")
        print(posthoc_ftd)
    else:
        print("No significant differences found between groupsfor frost table depth.")

    # Compare both main areas

    _, p_regions_vswc = scipy.stats.mannwhitneyu(
        gdfs_only_center[0].loc[:, "volumetric_soil_water_content"],
        gdfs_everything_else[0].loc[:, "volumetric_soil_water_content"]
        )
    _, p_regions_ftd = scipy.stats.mannwhitneyu(
        gdfs_only_center[1].loc[:, "calculated_depths_m"],
        gdfs_everything_else[1].loc[:, "calculated_depths_m"]
        )
    print(f"Mann-Whitney U test for volumetric soil water content: p = {p_regions_vswc}")
    print(f"Mann-Whitney U test for frost table depth: p = {p_regions_ftd}")
    print(" -------------------------------------------------------------------------------------------- ")
    # Print Table
    export_to_latex(
        data = results,
        caption = ("Results of Study Site-wide Analysis", "Mean and standard deviation for bulk volumetric soil water content (\\unit{\\cubic\\meter\\per\\cubic\\meter}) and Frost Table Depth (\\unit{\\meter}).\nEach value was calculated for different subareas.\nSignificant deviations were found using a Kruskal-Wallis test was combined with a Dunn's post-hoc analysis using the Holm-Bonferroni adjustment and a Mann-Whitney U test."),
        precision_dict = {},
        label = "tab:study_wide_results",
        float_placement_identifier = "ht",
        output_path = results_folder / "gpr_analysis" / Path("study_wide_results").with_suffix(".tex")
        )
    return None
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
