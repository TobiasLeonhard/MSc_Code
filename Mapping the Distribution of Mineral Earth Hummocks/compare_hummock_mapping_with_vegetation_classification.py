#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
compare_hummock_mapping_with_vegetation_classification.py

This script evaluates the relationship between mapped mineral earth hummocks and vegetation classes
by combining hummock and vegetation rasters, comparing their spatial overlap, and calculating the proportion
of each vegetation class within mapped hummock areas relative to the broader vegetation cover.
Results are summarized in a tabular output for interpretation and publication.

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
from utility_functions.combine_tifs import get_combined_raster
from utility_functions.python_to_latex import export_to_latex
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("compare_hummock_mapping_with_vegetation_classification.py started")
    # 1. Combine the mapped hummocks raster and the vegetation classification raster into a single multi-band raster
    # --------------------------------------------------- #
    # Define paths
    mapped_hummocks_path = results_folder / "hummock_mapping" / "dtm_mapping" / Path("mapped_hummocks_by_1x1_and_7x7_window_and_p_value_of_0p05_ with_area_between_1p5sqm_and_7p5sqm").with_suffix(".tif")
    vegetation_mapping_folder = results_folder / "vegetation_mapping" / "2023"
    vegetation_classification_path = vegetation_mapping_folder / Path("vegetation_classification_map_rf").with_suffix(".tif")
    output_dir = results_folder / "hummock_mapping_vegetation_classification_comparison"
    output_dir.mkdir(exist_ok = True)

    # Prepare the list of rasters to be combined
    my_rasters = [
        {
            "path":mapped_hummocks_path,
            "resampling": Resampling.nearest,
            "name": "Mapped Hummocks",
            "bands": [1]
            },
        {
            "path": vegetation_classification_path,
            "resampling": Resampling.mode,
            "name": "Vegetation Classification",
            "bands": [1]
            },
        ]
    # Combine the rasters into a single multi-band raster, ensuring they are aligned and have the same resolution
    nodata = 99
    combined_raster_path, rasters = get_combined_raster(
        input_rasters = my_rasters,
        target_resolution = "highest",
        nodata_value = nodata)

    # Read the combined raster and extract the relevant bands
    with rasterio.open(combined_raster_path) as dst:
        res_x, res_y = dst.res
        if res_x == res_y:
            res = res_x
        else:
            res = (res_x + res_y)/2
        hum_index = next((i for i, r in enumerate(rasters) if r["name"] == "Mapped Hummocks"), None)
        veg_index = next((i for i, r in enumerate(rasters) if r["name"] == "Vegetation Classification"), None)
        if hum_index is None or veg_index is None:
            raise ValueError("Could not find the required rasters in the combined raster.")
        data_hum = dst.read(hum_index + rasters[hum_index]["bands"][0])
        data_veg = dst.read(veg_index + rasters[veg_index]["bands"][0])

    # --------------------------------------------------- #
    # 2. Plot histograms of the vegetation classes for the mapped hummocks and for all valid vegetation pixels
    # --------------------------------------------------- #
    # Read the vegetation classes from the text file and create a mapping of class values to descriptions
    vegetation_classes_path = vegetation_mapping_folder / Path("class_legend_rf").with_suffix(".csv")
    # Read the vegetation classes from the text file
    df = pd.read_csv(vegetation_classes_path, sep=",")

    df.rename(columns={"Unnamed: 0": "vegetation_class_id", "Class Name": "vegetation_type"}, inplace=True)

    new_row = pd.DataFrame([{"vegetation_class_id": nodata, "vegetation_type": "No-Data"}])
    df = pd.concat([df, new_row], ignore_index=True)

    # Create a mapping of vegetation class values to their descriptions
    veg_class_mapping = dict(zip(df["vegetation_class_id"], df["vegetation_type"]))

    # Define two masks: one for pixels where hummocks are present (is_hummock_data) and one for all vegetation pixels (all_veg_data)
    hummock_mask = (data_hum == 1) & (data_veg != nodata)  # Mask for pixels where hummocks are present and vegetation is valid
    veg_mask = (data_veg != nodata)  # Mask for all valid vegetation pixels

    # Extract the vegetation of the mapped hummocks and the vegetation of all valid vegetation pixels
    vegetation_mapped_hummocks = data_veg[hummock_mask]
    vegetation_all = data_veg[veg_mask]

    # --------------------------------------------------- #
    # 3. Investigate the composition of the mapped hummocks in terms of vegetation classes and compare it to the overall vegetation composition
    # --------------------------------------------------- #
    df = pd.DataFrame(columns=["vegetation_class", "number_of_hummocks", "overall_number_of_pixels"])
    for veg_class_id, veg_class_name in veg_class_mapping.items():
        if veg_class_id == nodata:
            continue  # Skip the No-Data class
        df = pd.concat([
            df,
            pd.DataFrame({
                "vegetation_class": [veg_class_name],
                "number_of_hummocks": [np.sum(vegetation_mapped_hummocks == veg_class_id)],
                "overall_number_of_pixels": [np.sum(vegetation_all == veg_class_id)]
                })
            ],
            ignore_index=True
            )
    print(res)
    df["hummock_probability"] = (df["number_of_hummocks"] / df["number_of_hummocks"].sum())
    df["overall_probability"] = (df["overall_number_of_pixels"] / df["overall_number_of_pixels"].sum())


    print("-" * 50)
    report_df = df.drop(columns=["number_of_hummocks", "overall_number_of_pixels"])
    report_df.rename(columns={
        "vegetation_class": "Veg. Class",
        "hummock_probability": r"Veg. Cover of Mapped Hummocks ({\unit{\percent}})",
        "overall_probability": r"Overall Veg. Cover ({\unit{\percent}})"
        }, inplace=True)

    report_df[r"Veg. Cover of Mapped Hummocks ({\unit{\percent}})"] = report_df[r"Veg. Cover of Mapped Hummocks ({\unit{\percent}})"] * 100
    report_df[r"Overall Veg. Cover ({\unit{\percent}})"] = report_df[r"Overall Veg. Cover ({\unit{\percent}})"] * 100
    report = report_df[["Veg. Class", r"Veg. Cover of Mapped Hummocks ({\unit{\percent}})", r"Overall Veg. Cover ({\unit{\percent}})"]].copy()

    precision_dict = {
        r"Lichen": 1,
        r"Moss": 1,
        r"Shrub": 1,
        r"Tussock": 1,
        }

    export_to_latex(
        data = report,
        caption = ("Comparison of Hummock Mapping and Vegetation Mapping", "Comparison of Hummock Mapping and Vegetation Mapping\nVegetation is shorted to `Veg.'."),
        precision_dict = precision_dict,
        label = "tab:hummock_vegetation_mapping_comparison",
        float_placement_identifier = "ht",
        output_path = output_dir / Path("table_hummock_vegetation_mapping_comparison").with_suffix(".tif"),
        )

    print("\ncompare_hummock_mapping_with_vegetation_classification.py finished.")
    print("# ====================================================================================================================================================== #")
