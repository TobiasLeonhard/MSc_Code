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

Description:
This module implements the core hummock mapping algorithm and validation workflows.
It generates topographic position index products, applies statistical thresholding to identify hummock candidates, filters features by area and slope constraints, and validates mapped results against field-based ground truth using spatial matching and confusion matrix metrics.
The module produces both vector and raster hummock products and enables parametric sensitivity analysis.

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-14
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
from utility_functions.dtm_calculations import get_mean_elevation, get_smoothed_diff, get_thresholded_map, get_slope_map
from utility_functions.geo_vector_file_operations import polygonize_raster_to_vector
from utility_functions.active_layer_thickness import load_active_layer_data
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_tpi_histogram(data: pd.Series, fig_path: Path, z_score: float, title: str, x_label: str, x_unit: str, dpi: int, logarithmic: bool) -> Tuple[float , float, float]:
    """
    Plots the histrogram of a tpi data set.
    Returns mean and standard deviation of the data.
    Args:
        data - pd.Series: Pandas Series containing the flatten tpi values.
        z_score - float: P-Value used to calculate threshold
        fig_path - Path: Path where the figure is saved.
        title - str: Title of the figure.
        x_label - str: Text for the x axis label (excluding units).
        x_unit - str: Unit of the TPI values.
        dpi - int: DPI of the saved figure.
        logarithmic - bool: Sets the y axis as log.
    Returns:
        mean - float: Mean value
        std - float: Standard deviation
        threshold - float: Calculated Threshold
    """
    data = data.copy()
    # Clear for nans and infinities
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) == 0:
        raise ValueError("Given data is empty.")
    # Calculate mean and standard deviation
    mean = data.mean()
    std = data.std()
    threshold = z_score * std

    # Create labels for mean and std
    if round(mean, 4) == 0:
        mean = abs(mean)
    mean_label = rf"$\overline{{\text{{tpi}}}}$ = {mean:.4f} {x_unit}"
    std_label = rf"$\sigma_{{\text{{tpi}}}}$ = {std:.4f} {x_unit}"
    threshold_label = rf"$\tau$ = {threshold:.4f} {x_unit}"

    # Initiate Figure
    plt.figure(figsize=(8, 5))
    # Plot Histogram
    plt.hist(
        x = data,
        bins = 50,
        color = custom_colors["wlu_purple"],
        edgecolor = "black",
        log = logarithmic
        )
    # Plot excluding area
    plt.axvspan(
        data.min(),
        threshold,
        facecolor = "none",
        alpha = 0.2,
        hatch = "xxx",
        edgecolor = "black",
        label = "Excluded"
        )

    # Add lines for mean and +/- std
    plt.axvline(
        mean,
        color = "black",
        linestyle = "dashed",
        linewidth = 2,
        label = mean_label
        )
    plt.axvline(
        mean - std,
        color = "black",
        linestyle = "dotted",
        linewidth = 2,
        )
    plt.axvline(
        mean + std,
        color = "black",
        linestyle = "dotted",
        linewidth = 2,
        label = std_label
        )

    # Add threshold
    plt.axvline(
        threshold,
        color = "black",
        linestyle = "-",
        linewidth = 2,
        label = threshold_label
        )

    # Add aestetics
    plt.title(title)
    plt.xlabel(f"{x_label} ({x_unit})")
    plt.xlim(data.min(),  data.max())
    if logarithmic == True:
        plt.ylabel("Counted Occurences (in log. scale)")
    else:
        plt.ylabel("Counted Occurences")
    plt.legend()
    plt.tight_layout()

    # Save file and close plot
    fig_path.parent.mkdir(parents = True, exist_ok = True)
    plt.savefig(fig_path, dpi = dpi)
    plt.close()

    return mean, std, threshold

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def map_hummocks(dtm_path: Path, area_excluded_from_mapping: Path, output_dir: Path, target_crs: str, smooth_in_pixels: int, diff_mean_elev_interval_in_pixels: int, p_value: float, min_area_for_hummocks: float, max_area_for_hummocks: float, dpi: int) -> Path:
    """
    This function maps hummocks using a mean elevation - mean elevation approach.
    The threshold is calculated using the standard deviation of the mean of the calculated TPI.
    If the output file already exists, the process won't be run, but the file will just be returned
    Args:
        dtm_path - Path: Path to the unprocessed dtm file.
        area_excluded_from_mapping - Path: Path to the file that defines the areas that are excluded from hummock mapping
        output_dir - Path: Path to the output folder
        target_crs - str: CRS in which all outputs are saved in.
        smooth_in_pixels - int: Pixel window in which areas are smoothed (mean elevation) over (smooth_in_pixels = 3 -> 3x3 window)
        diff_mean_elev_interval_in_pixels  - int: Pixel window for which the different in mean elevation is calculated (diff_mean_elev_interval_in_pixels = 3 -> 3x3 window)
        p_value - float: One tailed p value used to define the z_score which is used to calculate the threshold of the tpi.
        min_area_for_hummocks - float: Min area to classify an anomaly as a hummock
        max_area_for_hummocks - float: Max area to classify an anomaly as a hummock
        dpi - int: DPI value
    Returns:
        mapped_hummocks_path - Path: Path to the mapped hummocks.
    """

    mapped_hummocks_path = output_dir / Path(f"mapped_hummocks_by_{smooth_in_pixels}x{smooth_in_pixels}_and_{diff_mean_elev_interval_in_pixels}x{diff_mean_elev_interval_in_pixels}_window_and_p_value_of_{str(p_value).replace('.', 'p')}_ with_area_between_{str(min_area_for_hummocks).replace('.', 'p')}sqm_and_{str(max_area_for_hummocks).replace('.', 'p')}sqm")
    diff_mean_elev_hist_path = output_dir / Path(f"{mapped_hummocks_path.stem}_histogram").with_suffix(".png")
    if not(mapped_hummocks_path.with_suffix(".gpkg").exists() and mapped_hummocks_path.with_suffix(".tif").exists()):
        z_score = scipy.stats.norm.ppf(1 - p_value)
        # Calculate the diff mean elevation
        diff_mean_elev_path = get_smoothed_diff(
            input_dtm = dtm_path,
            window_length_1 = smooth_in_pixels,
            window_length_2 = diff_mean_elev_interval_in_pixels
            )

        # Load data in a flat format to calculate mean, standard deviation, and get the resolution
        with rasterio.open(diff_mean_elev_path) as src:
            diff_mean_elev_data = pd.DataFrame({"tpi_values": src.read(1).flatten()})
            resolution = src.res[0]

        # Plot histrogram of the tpi_values
        mean, std, threshold = plot_tpi_histogram(
            data = diff_mean_elev_data["tpi_values"],
            fig_path = diff_mean_elev_hist_path,
            z_score = z_score,
            title = "Histogram of Difference of Mean Elevation Height",
            x_label = "Difference of Mean Elevation Height",
            x_unit = "m",
            dpi = dpi,
            logarithmic = True
            )

        # Callculate threshold by z_score
        threshold = z_score * std
        print(f"Found TPI mean: {mean} m with std of: {std}m")
        print(f"Calculated threshold for hummock TPI height: {threshold:.4f} m")

        # Create thresholded map, polygonize it, and load it as a gdf
        thresholded_map_path = get_thresholded_map(
            input_dtm = diff_mean_elev_path,
            threshold = threshold,
            threshold_type = "greater than"
            )

        polygonized_raster_path = polygonize_raster_to_vector(
            raster_path = thresholded_map_path,
            vector_path = thresholded_map_path.with_suffix(".gpkg"),
            connectivity = 4,
            values_are_boolean = True,
            property_key = "Is_Hummock"
            )

        hummock_data = gpd.read_file(polygonized_raster_path)

        # Select only the polygons that are above the threshold, calculate their area, and filter it by min and max area
        hummock_data = hummock_data[hummock_data["Is_Hummock"] == 1].copy()
        hummock_data["area"] = hummock_data.geometry.area
        hummock_data = hummock_data[(hummock_data["area"] >= min_area_for_hummocks) & (hummock_data["area"] <= max_area_for_hummocks)].copy()

        # Hummocks do not occur on slopes above 25 degrees (Grab 2005)
        slope_threshold = 25  # degrees
        smoothed_dtm = get_mean_elevation(
            input_dtm = dtm_path,
            window_length = 11
            )
        slope_path = get_slope_map(
            input_dtm = smoothed_dtm,
            units = "degrees",
            z_factor = 1
            )

        with rasterio.open(slope_path) as src:
            slope_crs = src.crs

        # Ensure CRS matches first
        if hummock_data.crs != slope_crs:
            hummock_data = hummock_data.to_crs(slope_crs)

        # Get the slope value for each hummock pixel
        stats = exactextract.exact_extract(slope_path, hummock_data, ["max"])
        if stats is not None:
            stats_list = cast(List[Dict[str, Any]], stats)
            hummock_data["slope_in_degree"] = [s["properties"]["max"] for s in stats_list]
        else:
            raise ValueError("Stats is none.")

        slope_cleaned_hummock_data = hummock_data[
            (hummock_data["slope_in_degree"] <= slope_threshold) &
            (hummock_data["slope_in_degree"].notna())
            ].copy()

        # Ensure correct CRS for rasterization
        target_crs = "EPSG:3155"
        if slope_cleaned_hummock_data.crs != target_crs:
            slope_cleaned_hummock_data = slope_cleaned_hummock_data.to_crs(target_crs)

        # Remove manual defined areas
        mask_gdf = gpd.read_file(area_excluded_from_mapping)
        if mask_gdf.crs != target_crs:
            mask_gdf = mask_gdf.to_crs(target_crs)

        cleaned_hummock_data = gpd.sjoin(
            slope_cleaned_hummock_data,
            mask_gdf,
            how = "left",
            predicate = "intersects"
            )
        cleaned_hummock_data = cleaned_hummock_data[cleaned_hummock_data["index_right"].isna()].copy()
        final_hummock_data = cleaned_hummock_data.drop(columns=["index_right"])

        final_hummock_data.to_file(
            mapped_hummocks_path.with_suffix(".gpkg"),
            driver = "GPKG",
            layer = "mapped_hummocks"
            )

        # Rasterize the data
        geo_grid = make_geocube(
            vector_data = final_hummock_data,
            measurements = ["Is_Hummock"],
            resolution = (-resolution, resolution),
            fill = 0
            )
        geo_grid["Is_Hummock"] = geo_grid["Is_Hummock"].rio.write_nodata(255)
        final_raster = geo_grid["Is_Hummock"].rio.clip(
            final_hummock_data.geometry,
            final_hummock_data.crs
            ).astype("uint8")
        final_raster.rio.to_raster(mapped_hummocks_path.with_suffix(".tif"), dtype = "uint8")
    return mapped_hummocks_path

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def load_ground_validation_data(output_dir: Path, target_crs: str) -> Path:
    """
    Loads or generates a GeoDataFrame of hummocks from field data.
    If the GeoDataFrame doesn't exist, create it by loading the field data and filtering for hummocks.

    Args:
        output_dir - Path: Output folder
        target_crs - str: String of the targes CRS
    Returns:
        ground_validation_data_path - Path: Path to the cleaned in situ data
    """
    ground_validation_data_path = output_dir / Path(f"ground_validated_microtopography_classification_in_{target_crs.replace(':','')}").with_suffix(".gpkg")
    if not ground_validation_data_path.exists():
        # Load frozen table depth data
        frozen_table_depth_data = load_active_layer_data()
        # Only keep data from the Siksik study sites
        frozen_table_depth_data = frozen_table_depth_data[frozen_table_depth_data["study_site_id"].str.contains("Siksik") == True].copy()

        # Introduce new column "is_hummock", set it to 1 for Hummocks and to 0 for everything else
        frozen_table_depth_data["is_hummock"] = 0
        frozen_table_depth_data.loc[frozen_table_depth_data["assigned_topographic_feature"] == "H", "is_hummock"] = 1

        frozen_table_depth_data["is_interhummock"] = 0
        frozen_table_depth_data.loc[frozen_table_depth_data["assigned_topographic_feature"] == "IH", "is_interhummock"] = 1

        # Remove "assigned_topographic_feature" column
        ground_validation_data = frozen_table_depth_data[["is_hummock", "is_interhummock", "geometry", "study_site_id"]]
        ground_validation_data = ground_validation_data.to_crs(target_crs)
        ground_validation_data.to_file(ground_validation_data_path, layer = "rtk_points", driver = "GPKG")

    return ground_validation_data_path

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def evaluate_mapping_results(mapped_hummocks_path: Path, ground_validation_data_path: Path, detection_radius_hummock: float, detection_radius_interhummock: float, target_crs: str) -> dict:
    """
    This function evaluates the mapping results by comparing the mapped hummocks from the polygonized raster with the mapped hummocks and other features from the field data.
    The function calculates the true positives, false positives, and false negatives based on a specified detection radius, and then computes the precision, recall, and F1 score for the mapping results.
    Args:
        mapped_hummocks_path - Path: Path to the mapped hummocks from the polygonized raster
        mapped_hummocks_field_path - Path: Path to the mapped hummocks from the field data
        mapped_others_field_path - Path: Path to the mapped other features from the field data
        detection_radius_hummock - float: Detection radius in meter for detecting a hummock
        detection_radius_interhummock - float: Detection radius in meter for detecting an interhummock
    Returns:
        metrics - dict: A dictionary containing the true positives, false positives, false negatives, precision, recall, and F1 score.
    """
    # -------------------------------- #
    # Load the mapped hummocks from the polygonized raster and the field data
    mapped_hummocks = gpd.read_file(mapped_hummocks_path.with_suffix(".gpkg"))
    ground_validation_data = gpd.read_file(ground_validation_data_path.with_suffix(".gpkg"))

    # Remove empty geometries
    mapped_hummocks = mapped_hummocks[mapped_hummocks.geometry.notna() & ~mapped_hummocks.geometry.is_empty].copy()
    ground_validation_data = ground_validation_data[ground_validation_data.geometry.notna() & ~ground_validation_data.geometry.is_empty].copy()

    # Check whether any data is empty, and if so, use nan for everything
    if mapped_hummocks.empty or ground_validation_data.empty:
        print("One or more of the datasets is empty. Returning 0 for all metrics.")
        metrics = {
            "True Positives": np.nan,
            "False Positives": np.nan,
            "False Negatives": np.nan,
            "True Negatives": np.nan,
            "Chi-Square Statistic": np.nan,
            "P-value of Chi-Square Statistic": np.nan,
            "Cohen's Kappa": np.nan
            }
    else:
        # Make sure that both CRS are the same
        mapped_hummocks = mapped_hummocks.to_crs(target_crs)
        ground_validation_data = ground_validation_data.to_crs(target_crs)

        # Clean possible double classifications:
        ground_validation_data = ground_validation_data[~((ground_validation_data["is_hummock"] == 1) & (ground_validation_data["is_interhummock"] == 1))]

        # Separate the ground validation data by hummocks and not hummocks
        ground_validation_data_hummocks = ground_validation_data[ground_validation_data["is_hummock"] == 1]
        ground_validation_data_hummocks = ground_validation_data_hummocks.set_geometry(ground_validation_data_hummocks.geometry.buffer(detection_radius_hummock))

        ground_validation_data_not_hummocks = ground_validation_data[ground_validation_data["is_hummock"] == 0]
        ground_validation_data_not_hummocks = ground_validation_data_not_hummocks.set_geometry(ground_validation_data_not_hummocks.geometry.buffer(detection_radius_hummock))

        ground_validation_data_interhummocks = ground_validation_data[ground_validation_data["is_interhummock"] == 1]
        ground_validation_data_interhummocks = ground_validation_data_interhummocks.set_geometry(ground_validation_data_not_hummocks.geometry.buffer(detection_radius_interhummock))

        ground_validation_data_neither = ground_validation_data_not_hummocks[ground_validation_data_not_hummocks["is_interhummock"] == 0]
        ground_validation_data_neither = ground_validation_data_neither.set_geometry(ground_validation_data_neither.geometry.buffer(detection_radius_interhummock))

        n_hummock_points = len(ground_validation_data_hummocks)
        n_not_hummock_points = len(ground_validation_data_not_hummocks)

        # Calculate true positives -> intersection of hummocks and mapped hummocks
        true_positives = len(gpd.sjoin(ground_validation_data_hummocks, mapped_hummocks, predicate = "intersects", how = "inner").index.unique())

        # Calculate false positives ->  intersection of not hummocks and mapped hummocks
        false_positives = len(gpd.sjoin(ground_validation_data_not_hummocks, mapped_hummocks, predicate = "intersects", how = "inner").index.unique())

        # Calculate the false negatives -> we do a inner sjoin and see where we could not find anything
        # Find the indices of everything that DOES intersect
        intersecting_indices = gpd.sjoin(
            ground_validation_data_hummocks,
            mapped_hummocks,
            how = "inner",
            predicate = "intersects"
            ).index.unique()

        # False negatives are the rows NOT in that list of indices
        false_negatives_df = ground_validation_data_hummocks[~ground_validation_data_hummocks.index.isin(intersecting_indices)]
        false_negatives = len(false_negatives_df)

        # True Negatives calculation
        not_hummock_intersecting = gpd.sjoin(ground_validation_data_not_hummocks, mapped_hummocks, predicate="intersects", how="inner").index.unique()
        true_negatives = n_not_hummock_points - len(not_hummock_intersecting)

        # Calculate precision, recall and f1 score
        table = [
            [true_positives, false_positives],
            [false_negatives, true_negatives]
            ]

        chi2, p, dof, expected = chi2_contingency(table)

        kappa_y_true = [1] * n_hummock_points + [0] * n_not_hummock_points
        kappa_y_pred = [1] * true_positives + [0] * false_negatives + [1] * false_positives + [0] * true_negatives
        kappa = cohen_kappa_score(kappa_y_true, kappa_y_pred)

        metrics = {
            "True Positives": true_positives,
            "False Positives": false_positives,
            "False Negatives": false_negatives,
            "True Negatives": true_negatives,
            "Chi-Square Statistic": chi2,
            "P-value of Chi-Square Statistic": p,
            "Cohen's Kappa": kappa
            }

    return metrics

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
