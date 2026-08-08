#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
hummock_mapping.py

This file handles all hummock mapping processes.
It creates different hummock maps using the DTM from the KBM LIDAR campaing 2024

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
from config.environment import *
from utility_functions.hummock_mapping import map_hummocks, load_ground_validation_data, evaluate_mapping_results
from utility_functions.python_to_latex import export_to_latex
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("hummock_mapping.py started")
    # ----------------------------------------------------------------------------------------------- #
    # ------------------------------- #
    # Define constants and parameters for the analysis
    # ------------------------------- #
    # Path to the DTM
    dtm_path = data_folder / "tvc_data" / "mapping" / Path("2024 - LIDAR - DTM - Siksik").with_suffix(".tif")
    output_dir = results_folder / "hummock_mapping" / "dtm_mapping"
    output_dir.mkdir(exist_ok = True, parents = True)
    area_excluded_from_mapping = manual_input_folder / Path("excluded_areas_from_hummock_mapping").with_suffix(".gpkg")

    target_crs = "EPSG:3155"
    # ----------------------------------------------------------------------------------------------- #
    min_area_for_hummocks_list = np.array([1, 1.5]) # Minimum area for mapped hummocks in square meters, to exclude small features that are unlikely to be hummocks
    max_area_for_hummocks_list = np.array([7.5]) # Maximum area for mapped hummocks in square meters, to exclude large features that are unlikely to be hummocks
    p_values = np.array([0.05, 0.1])

    smooth_in_pixels_list = np.array([1])
    diff_mean_elev_interval_in_pixels_list = np.array([7])

    mapped_hummocks = {}
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Map hummocks")
    for min_area_for_hummocks in min_area_for_hummocks_list:
        for max_area_for_hummocks in max_area_for_hummocks_list:
            if min_area_for_hummocks >= max_area_for_hummocks:
                continue
            for p_value in p_values:
                for smooth_in_pixels in smooth_in_pixels_list:
                    for diff_mean_elev_interval_in_pixels in diff_mean_elev_interval_in_pixels_list:
                        if smooth_in_pixels == diff_mean_elev_interval_in_pixels:
                            # This would just make 0 everywhere
                            continue
                        elif smooth_in_pixels == 1 and diff_mean_elev_interval_in_pixels == 3:
                            # This makes nearly 0 everywhere
                            continue
                        else:
                            print(f"Processing for p value {p_value} with a smoothing window of {smooth_in_pixels}x{smooth_in_pixels} and a diff window of {diff_mean_elev_interval_in_pixels}x{diff_mean_elev_interval_in_pixels} with a min area of {min_area_for_hummocks} sqm and a max area of {max_area_for_hummocks} sqm.")
                            mapped_hummocks_path = map_hummocks(
                                dtm_path = dtm_path,
                                area_excluded_from_mapping = area_excluded_from_mapping,
                                output_dir = output_dir,
                                target_crs = target_crs,
                                smooth_in_pixels = smooth_in_pixels,
                                diff_mean_elev_interval_in_pixels = diff_mean_elev_interval_in_pixels,
                                p_value = p_value,
                                min_area_for_hummocks = min_area_for_hummocks,
                                max_area_for_hummocks = max_area_for_hummocks,
                                dpi = DPI
                                )
                            mapped_hummocks[(smooth_in_pixels, p_value, diff_mean_elev_interval_in_pixels, min_area_for_hummocks, max_area_for_hummocks)] = mapped_hummocks_path
                            print("")

    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Evaluation of Mapping Results")
    # Load the ground_validation_data
    ground_validation_data_path = load_ground_validation_data(
            output_dir = output_dir,
            target_crs = target_crs
            )
    highest_kappa = 0
    highest_chi_square = 0
    metrics_list = []
    for key, path in mapped_hummocks.items():
        metrics = evaluate_mapping_results(
            mapped_hummocks_path = path,
            ground_validation_data_path = ground_validation_data_path,
            detection_radius_hummock = 1,
            detection_radius_interhummock = 0.25,
            target_crs = target_crs
            )
        metrics["p-value"] = key[1]
        metrics["Min. Area"] = key[3]
        metrics_list.append(metrics)


    report = pd.DataFrame(metrics_list)
    report["Settings"] = ("Used p-Value of " + report["p-value"].map(str) + " with an \\\\ Min. Area of {\\qty{" + report["Min. Area"].map(str) + "}{\\square\\meter}}")
    report.drop(
        columns=[
            "p-value", "Min. Area"
            ],
        inplace=True)
    report.rename(
        columns={
            "Chi-Square Statistic": "Chi-Square",
            "P-value of Chi-Square Statistic": "p-Value of Chi-Square"
            },
        inplace=True
        )
    report = pd.melt(report,
                  id_vars = ["Settings"],
                  value_vars = ["True Positives", "False Positives", "False Negatives", "True Negatives", "Chi-Square", "p-Value of Chi-Square", "Cohen's Kappa"],
                  var_name = "Metric",
                  value_name = "Calculated Value")
    report = report.pivot(
        index = "Metric",
        columns = "Settings",
        values = "Calculated Value"
        )
    order = ["True Positives", "False Positives", "False Negatives", "True Negatives", "Chi-Square", "p-Value of Chi-Square", "Cohen's Kappa"]
    report = report.sort_values(
        by = "Metric",
        key = lambda x: x.map({val: i for i, val in enumerate(order)})
        )
    report = report.reset_index()
    report.columns.name = None
    precision_dict = {
        "True Positives": 0,
        "False Positives": 0,
        "False Negatives": 0,
        "True Negatives": 0,
        "Chi-Square": 2,
        "p-Value of Chi-Square": 7,
        "Cohen's Kappa": 3
        }
    export_to_latex(
        data = report,
        caption = ("Validaiton Metrics of Hummock Mapping", "This table shows the discussed validation metrics for the two investigated p-values, a minimum area of \\qty{1.5}{\\square\\meter}, and a detection radius of \\qty{1.5}{\\meter}.\nHowever, the metrics for other detection radii and minimum areas are similar.\nThe highly significant p-values ($p < 0.001$) across all Chi-Square tests confirms that the models have captured a non-random relationship and are performing better than chance.\nHowever, the low Cohen's Kappa values indicate that this signal is too weak for reliable classification.\nThis suggests a that input data with higher quality is needed or potential inconsistencies in the validation data."),
        precision_dict = precision_dict,
        label = "tab:hummock_mapping_validation",
        float_placement_identifier = "ht",
        output_path = output_dir / Path("metrics_report").with_suffix(".tif"),
        )
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\nhummock_mapping.py finished.")
    print("# ====================================================================================================================================================== #")
