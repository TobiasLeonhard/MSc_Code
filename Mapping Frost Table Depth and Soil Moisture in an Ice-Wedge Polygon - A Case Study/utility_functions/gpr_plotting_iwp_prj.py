#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
gpr_plotting.py

This file contains functions for plotting GPR related data

Author: Tobias Leander Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-06
"""
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment_iwp_prj import *
from config.environment import *
from utility_functions.combine_tifs import get_combined_raster
from utility_functions.gnss_handling import load_control_points
from utility_functions.gpr_plotting import adjust_cut_width_based_on_transect_length, plot_gpr_traces, add_enumaration_to_subplot, add_identification_to_plot, plot_active_layer_on_gpr_trace, adjust_x_tick_labels_and_grid, plot_volumetric_soil_water_content, plot_calculated_depth, plot_elevation_profile_and_active_layer_thickness, plot_tif_background_with_gpr_trace, handle_legend_entrances, provide_title_from_sgy_path, save_transect_data_to_parquet, points_to_segments
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_transect_wise_in_IWP_setting(transect_data: gpd.GeoDataFrame, image_data: dict, used_velocities_m_ns: dict, pck_file: Path, cut_half_width_m: float = 10.0, fig_width_cm: float = 30, height_unit_cm: float = 7.5, dpi: int = 300) -> None:
    """
    Plots GPR results transect wise for the IWP site

    Args:
        transect_data - gpd.GeoDataFrame: Data frame containing the needed GPR data.
        image_data - dict: Dictionary containing plotting information.
        used_velocities_m_ns - dict: Dictionary of used velocities.
        pck_file - Path: Path of the used pick file
        cut_half_width_m - float: Half-width in meters for cropping the orthomosaic around the transect. Defaults to 10.0
        fig_width_cm - float: Width of the figure in cm. Defaults to 30.
        height_unit_cm - float: Height of each unit (standard panel) in cm. Defaults to 7.5
        dpi - int: DPI value. Defaults to 300
    """
    # Define height ratios and order of axes
    legend_axis = [0, 0.75]
    radiogram_axis_0 = [1, 0.9]
    radiogram_axis_1 = [2, 0.9]
    radiogram_axis_2 = [3, 0.9]
    frozen_layer_axis = [4, 0.6]
    tiff_axis = [5, 1.3]

    height_ratios = [
        legend_axis[1],
        radiogram_axis_0[1],
        radiogram_axis_1[1],
        radiogram_axis_2[1],
        frozen_layer_axis[1],
        tiff_axis[1]
        ]

    # Convert to inches for matplotlib
    fig_width = fig_width_cm / 2.54
    fig_height = height_unit_cm * sum(height_ratios) / 2.54

    # Update cut_half_width
    updated_cut_half_width_m = adjust_cut_width_based_on_transect_length(cut_half_width_m, transect_data, fig_width, height_unit_cm, height_ratios)

    # Initiate figure
    fig = plt.figure(figsize = (fig_width, fig_height))
    gs = gridspec.GridSpec(len(height_ratios), 1, height_ratios = height_ratios, hspace = 0.3)

    axes = [fig.add_subplot(gs[i, 0]) for i in range(len(height_ratios))]

    # Plot 1. subplot legend_axis -> Turn it off.
    axes[legend_axis[0]].axis("off")

    # Plot 2. subplot radiogram_axis_0: GPR traces with surface topography correction
    axes[radiogram_axis_0[0]] = plot_gpr_traces(
        ax = axes[radiogram_axis_0[0]],
        transect_data = transect_data,
        trace_column = "trace_values_with_surface_topography",
        title = None
        )
    axes[radiogram_axis_0[0]] = add_enumaration_to_subplot(
        ax = axes[radiogram_axis_0[0]],
        enumaration = "(a)"
        )

    # Plot 3. subplot radiogram_axis_1: GPR traces with ground selection and active layer thickness points
    axes[radiogram_axis_1[0]] = plot_gpr_traces(
        ax = axes[radiogram_axis_1[0]],
        transect_data = transect_data,
        trace_column = "trace_values",
        title = None,
        y_label = "Depth (m)"
        )
    axes[radiogram_axis_1[0]], _ = add_identification_to_plot(
        ax = axes[radiogram_axis_1[0]],
        transect_data = transect_data,
        x_col = "distance_from_starting_pos_m",
        y_col = "refl_line_travel_times_ns",
        linewidth = 5,
        identification_col = "volumetric_soil_moisture_classification"
        )
    axes[radiogram_axis_1[0]] = plot_active_layer_on_gpr_trace(
        ax = axes[radiogram_axis_1[0]],
        transect_data = transect_data,
        used_velocities_m_ns = used_velocities_m_ns
        )
    # Adjust x-tick labels and grid
    axes[radiogram_axis_1[0]] = adjust_x_tick_labels_and_grid(
        ax = axes[radiogram_axis_1[0]]
        )
    axes[radiogram_axis_1[0]] = add_enumaration_to_subplot(
        ax = axes[radiogram_axis_1[0]],
        enumaration = "(b)"
        )

    # Plot 4. subplotradiogram_axis_2: Plot calculated depth profile and volumetric soil water content
    axes[radiogram_axis_2[0]], colorbar_info = plot_volumetric_soil_water_content(
        ax = axes[radiogram_axis_2[0]],
        transect_data = transect_data
        )
    axes[radiogram_axis_2[0]] = plot_calculated_depth(
        ax = axes[radiogram_axis_2[0]],
        transect_data = transect_data
        )
    axes[radiogram_axis_2[0]] = add_enumaration_to_subplot(
        ax = axes[radiogram_axis_2[0]],
        enumaration = "(c)")

    # Plot 5. subplot frozen_layer_axis: Plotb elevation profile (third subplot)
    axes[frozen_layer_axis[0]] = plot_elevation_profile_and_active_layer_thickness(
        ax = axes[frozen_layer_axis[0]],
        transect_data = transect_data)
    axes[frozen_layer_axis[0]] = add_enumaration_to_subplot(
        ax = axes[frozen_layer_axis[0]],
        enumaration = "(d)"
        )

    # Plot 6. subplottiff_axis: Orthomosaic with GPS trace and active layer points
    axes[tiff_axis[0]] = plot_tif_background_with_gpr_trace(
        ax = axes[tiff_axis[0]],
        ax_ticks = axes[radiogram_axis_0[0]],
        transect_data_for_plotting = image_data,
        transect_data = transect_data,
        use_rasters = ["aerial_map", "trough_map"],
        y_margin = updated_cut_half_width_m,
        add_active_layer = True,
        identification_col = "volumetric_soil_moisture_classification"
        )
    axes[tiff_axis[0]] = add_enumaration_to_subplot(axes[tiff_axis[0]], "(e)")

    # Done with plotting, now improve visuals and save
    fig.canvas.draw()  # Ensure the figure is rendered

    # Handle the legend
    desired_legend_order = [
        ["Identified as Dry Area", "Identified as Wet Area", "Identified as Moist Area"], # Values for the first column in the legend
        ["Measured Frozen Table Depth", "Calculated Frozen Table Depth", "Frozen Table Probing Location"], # Values for the second column in the legend
        ["GPR Trace from GPS", "Surface Elevation", "Mapped Trough"],# Values for the third column in the legend
        ["Frozen Layer", "Thawed Layer"] # Value for the fourth column in the legend
        ]
    axes[legend_axis[0]] = handle_legend_entrances(
        axes = axes,
        axis = axes[legend_axis[0]],
        legend_order = desired_legend_order
        )

    # Done with legend, render the figure
    fig.canvas.draw()

    # Add the colorbar
    # [left, bottom, width, height]
    cax = axes[legend_axis[0]].inset_axes([0.03, 0, 0.94, 0.2])
    cax.set_zorder(10)
    vmin = colorbar_info.norm.vmin
    if vmin is None:
        vmin = 0.0
    elif isinstance(vmin, tuple):
        vmin = vmin[0]
    if vmin < 0:
        vmin = 0
    vmax = colorbar_info.norm.vmax
    if vmax is None:
        vmax = 0.0
    elif isinstance(vmax, tuple):
        vmax = vmax[0]
    v_ticks = np.arange(vmin, vmax + 0.2, 0.2)
    cbar = fig.colorbar(
        colorbar_info,
        cax = cax,
        orientation = "horizontal",
        ticks = v_ticks
        )
    cbar.ax.set_xticklabels([f"{tick:.2f}" for tick in v_ticks])
    cbar.set_label(
        "Bulk Volumetric Soil Water Content (m³m⁻³)",
        labelpad = -60,
        fontsize = legend_fontsize
        )

    # Done with the colorbar, render the figure
    fig.canvas.draw()


    # Adjust the figure main title
    # Get unique dates in Inuvik timezone
    gpr_date = transect_data["datetime_utc"].dt.tz_convert("America/Inuvik").dt.date.unique()[0]

    overall_title, _ = provide_title_from_sgy_path(
        pck_file = pck_file,
        gdf = transect_data,
        gpr_date = gpr_date
        )
    fig.suptitle(overall_title, y=0.98)

    # Adjust layout and save
    plt.subplots_adjust(left=0.08, right=0.98, top=0.96, bottom=0.08)

    # Save plot
    save_path = results_folder / "gpr_analysis" / pck_file.stem
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        save_path.with_suffix(".png"),
        dpi = dpi,
        bbox_inches = "tight",
        pad_inches = 0.2
        )

    # Close the figure to free memory
    plt.close(fig)

    # Save the transect data with all added information to a parquet file for future use
    geometry_cols = [("geometry_from_active_layer_data", "active_layer_data")]
    save_transect_data_to_parquet(
        data = transect_data,
        path = save_path,
        geometry_cols = geometry_cols
        )
    return None

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_subtransect_of_IWP_transect(start_point: Union[int, float], end_point: Union[int, float], transect_data: gpd.GeoDataFrame, image_data: dict, pck_file: Path, cut_half_width_m: float = 10.0, fig_width_cm: float = 30, height_unit_cm: float = 7.5, dpi: int = 300) -> None:
    """
    Plots GPR results in subtransects for the IWP site

    Args:
        start_point - Union[int, float]: Start of subtransect
        end_point - Union[int, float]: End of subtransect
        transect_data - gpd.GeoDataFrame: Data frame containing the needed GPR data.
        image_data - dict: Dictionary containing plotting information.
        pck_file - Path: Path of the used pick file
        cut_half_width_m - float: Half-width in meters for cropping the orthomosaic around the transect. Defaults to 10.0
        fig_width_cm - float: Width of the figure in cm. Defaults to 30.
        height_unit_cm - float: Height of each unit (standard panel) in cm. Defaults to 7.5
        dpi - int: DPI value. Defaults to 300
    """
    if start_point >= end_point:
                raise ValueError("Invalid subtransect points: start point should be less than end point.")
    # Filter the transect data for the specified subtransect
    transect_data_sub = transect_data[(transect_data["distance_from_starting_pos_m"] >= start_point) & (transect_data["distance_from_starting_pos_m"] <= end_point)].reset_index(drop=True)
    transect_data_sub["transect_cropped"] = True
    if transect_data_sub.empty:
        raise ValueError("The specified subtransect does not contain any data points. Please check the provided start and end points.")
    # Now we can build the figure for the subtransect using the same code as above, but replacing transect_data with transect_data_sub
    # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    spacer_axis_0 = [0, 0.1]
    legend_axis = [1, 0.3]
    radiogram_axis_0 = [2, 0.9]
    spacer_axis_1 = [3, 0.1]
    tiff_axis = [4, 1.3]

    height_ratios = [
        spacer_axis_0[1],
        legend_axis[1],
        radiogram_axis_0[1],
        spacer_axis_1[1],
        tiff_axis[1]
        ]

    # Convert to inches for matplotlib
    fig_width = fig_width_cm / 2.54
    fig_height = height_unit_cm * sum(height_ratios) / 2.54

    # Update cut_half_width
    updated_cut_half_width_m = adjust_cut_width_based_on_transect_length(
        cut_half_width = cut_half_width_m,
        data = transect_data_sub,
        fig_width = fig_width,
        height_unit_cm = height_unit_cm,
        height_ratios = height_ratios
        )

    fig = plt.figure(figsize = (fig_width, fig_height))
    gs = gridspec.GridSpec(len(height_ratios), 1, height_ratios = height_ratios, hspace = 0.3)

    axes = [fig.add_subplot(gs[i, 0]) for i in range(len(height_ratios))]
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------------------------------#
    # Plot 1. subplot legend_axis: Empty space for legend
    axes[legend_axis[0]].axis("off")
    axes[spacer_axis_0[0]].axis("off")
    axes[spacer_axis_1[0]].axis("off")
    # ------------------------------------------------------------------#
    # Plot 2. subplot (axes[1]): GPR traces with ground selection and active layer thickness points
    axes[radiogram_axis_0[0]] = plot_gpr_traces(
        ax = axes[radiogram_axis_0[0]],
        transect_data = transect_data_sub,
        trace_column = "trace_values",
        title = None,
        y_label = "Depth (m)"
        )

    axes[radiogram_axis_0[0]] = add_enumaration_to_subplot(
        ax = axes[radiogram_axis_0[0]],
        enumaration = "(a)"
        )
    axes[radiogram_axis_0[0]] = adjust_x_tick_labels_and_grid(
        ax = axes[radiogram_axis_0[0]],
        ticks_interval = 1
        )
    axes[radiogram_axis_0[0]].set_xlabel("Distance from starting position (m)")
    axes[radiogram_axis_0[0]].xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    axes[radiogram_axis_0[0]].grid(True, which = "both", axis = "x", linestyle = "--", linewidth = 0.5)
    # ------------------------------------------------------------------#
    # Plot 3. subplot (axes[2]): Orthomosaic with GPS trace and active layer points
    axes[tiff_axis[0]] = plot_tif_background_with_gpr_trace(
        ax = axes[tiff_axis[0]],
        ax_ticks = axes[radiogram_axis_0[0]],
        transect_data_for_plotting = image_data,
        transect_data = transect_data_sub,
        use_rasters = ["aerial_map", "trough_map"],
        y_margin = updated_cut_half_width_m,
        add_active_layer = False,
        identification_col = "volumetric_soil_moisture_classification"
        )
    axes[tiff_axis[0]] = add_enumaration_to_subplot(
        ax = axes[tiff_axis[0]],
        enumaration = "(b)"
        )

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # Done with plotting, now improve visuals and save
    fig.canvas.draw()
    # Now we want to adjust the legends by plotting them outside of the axes
    handles = []
    labels = []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()
    by_label = dict(zip(labels, handles))
    # We want to adjust the legend layout so that it is nicely within the margins of our plot
    axes[legend_axis[0]].legend(by_label.values(), by_label.keys(), loc="lower center", ncol=4)
    fig.canvas.draw()  # Redraw to update legend
    # -------------------------------------------------------------------#
    # Adjust the figure main title
    # Get unique dates in Inuvik timezone
    gpr_date = transect_data["datetime_utc"].dt.tz_convert("America/Inuvik").dt.date.unique()[0]

    overall_title, _ = provide_title_from_sgy_path(
        pck_file = pck_file,
        gdf = transect_data_sub,
        gpr_date = gpr_date
        )
    fig.suptitle(overall_title, y=0.98)

    # Adjust layout and save
    plt.subplots_adjust(left=0.08, right=0.98, top=0.96, bottom=0.08)

    # Save plot
    save_path = results_folder / "gpr_analysis" / (pck_file.stem + f"_subtransect_{start_point}_{end_point}")
    save_path.parent.mkdir(parents = True, exist_ok = True)
    fig.savefig(
        save_path.with_suffix(".png"),
        dpi = dpi,
        bbox_inches = "tight",
        pad_inches = 0.2
        )

    # Close the figure to free memory
    plt.close(fig)

    # Save the transect data with all added information to a parquet file for future use
    geometry_cols = [("geometry_from_active_layer_data", "active_layer_data")]
    save_transect_data_to_parquet(
        data = transect_data_sub,
        path = save_path,
        geometry_cols = geometry_cols
        )
    return None

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_whole_iwp_figure(gdf: gpd.GeoDataFrame, input_rasters: dict, save_path: Path, plot_overlay: dict, title: str, subtransect_rectangles: list = [], dpi: int = 300, buffer: int = 50, wanted_epsg_crs: int = 3155) -> Tuple[dict, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
        Creates a figure visualizing the whole IWP GeoDataFrame with a background from a given TIFF file, and saves it to the specified path.
    Args:
        gdf - gpd.GeoDataFrame: GeoDataFrame containing the IWP data to be visualized.
        input_rasters - dict: List containing the tif file and a dictionary mapping band names to their corresponding indices in the tif file.
        save_path - Path: Path where the resulting figure will be saved.
        plot_overlay - dict: Dictionary containing the column name and label for the plot overlay.
        title - str: Title for the figure.
        subtransect_rectangles - list: A list of subtransect rectangles. Defaults to []
        dpi - int: Resolution of the saved figure in dots per inch. Defaults to 300.
        buffer - int: Buffer in meters to apply around the bounds of the GeoDataFrame for cropping the TIFF file. Defaults to 50.+
        wanted_epsg_crs - int: Wanted EPSG code. Defaults to 3155

    Returns:
        results - dict: Results of the comparison between IWP study site center and edge area
        gdf_only_center - gpd.GeoDataFrame: Dataframe containing data of 'subsidence free' center
        gdf_everything_else - gpd.GeoDataFrame: Dataframe containing data of the surrounding area
    """
    gdf = gdf.to_crs(epsg = wanted_epsg_crs)  # Reproject gdf to the wanted CRS for consistent processing and visualization
    subsidence_free_center_path = manual_input_folder / Path("area_defined_as_subsidence_free_center").with_suffix(".gpkg")
    subsidence_free_center = gpd.read_file(subsidence_free_center_path)

    combined_tif_file, sorted_rasters = get_combined_raster(
        input_rasters = input_rasters,
        target_epsg = wanted_epsg_crs,
        target_resolution = "highest",
        ensure_equal_resolution = False,
        buffer_size_m = buffer
        )
    value_cols = list(plot_overlay.keys()) + ["iwp_mapping_values"]
    gdf = points_to_segments(
        gdf = gdf,
        value_cols = value_cols,
        sort_cols = ["transect_name", "distance_from_starting_pos_m"],
        smoothing_window = 60
        )  # Transform points to segments for better visualization

    gdf_only_center =  gpd.clip(gdf, subsidence_free_center)
    gdf_everything_else = gpd.overlay(gdf, subsidence_free_center, how = "difference")
    bounds = gdf.total_bounds

    rds = rioxarray.open_rasterio(combined_tif_file, masked = True)
    if isinstance(rds, list):
        rds = rds[0]
    rds_cropped = rds.rio.clip_box(
        bounds[0] - buffer, bounds[1] - buffer,
        bounds[2] + buffer, bounds[3] + buffer
        )

    control_points = load_control_points()
    iwp_points = control_points[control_points["study_site_id"].str.contains("IWP", na = False)]
    iwp_points.crs = gdf.crs

    print("TIFF file loaded and cropped to the bounds of the GeoDataFrame with an additional buffer.")

    left, bottom, right, top = rds_cropped.rio.bounds()
    img_extent = [left, right, bottom, top]
    # --------------------------------------------------------------
    # Now the data preparation is done, we can build the figure
    # Initialize figure
    fig_width_cm = 21
    fig_width = fig_width_cm / 2.54
    fig_height_cm = 21
    fig_height = fig_height_cm / 2.54


    legend_axis = [0, 0.1]
    spacer_axis_0 = [1, 0.05]
    colorbar_axis = [2, 0.05]
    spacer_axis_1 = [3, 0.1]
    tiff_axis = [4, 1.3]

    height_ratios = [legend_axis[1], spacer_axis_0[1], colorbar_axis[1], spacer_axis_1[1], tiff_axis[1]]

    fig = plt.figure(figsize = (fig_width, fig_height))
    gs = gridspec.GridSpec(len(height_ratios), 1, height_ratios = height_ratios, hspace = 0)

    axes = [fig.add_subplot(gs[i, 0]) for i in range(len(height_ratios))]
    # --------------------------------------------------------------
    # 1. Add image background
    z_order = 0
    used_bands = 0

    for _, raster in input_rasters.items():
        # ---------------------------------------------------------------------------------------------------------- #
        # Decide on the bands - image data
        # Get image data for the specified band(s) in the background list, and process it accordingly depending on whether it's RGB or single band data
        use_bands = [band + used_bands for band in raster["bands"]]
        if len(use_bands) > 1:
            # We have multiple bands, so we assume it's RGB and we need to process it accordingyl
            img_data = rds_cropped.sel(band = use_bands).values.transpose(1, 2, 0)
            img_data = np.nan_to_num(img_data)
            if img_data.max() > 1.0:
                img_data = img_data / 255.0  # Normalize to [0, 1] if the data is in [0, 255]
            img_data = np.clip(img_data, 0, 1)  # Ensure values are within [0, 1]
        elif len(use_bands) == 1:
            # We assume we have mapping data, so we process it as a single band and we will add it as a transparent overlay later
            img_data = rds_cropped.sel(band = use_bands[0]).values.squeeze()
            img_data = np.nan_to_num(img_data, nan = 0).astype(np.uint8)
        else:
            raise ValueError("The provided band names in the image_background list do not seem to be valid. Please provide valid band names corresponding to the bands in the TIFF file.")

        used_bands += len(use_bands)  # Update the count of used bands to ensure we select the correct bands for subsequent backgrounds

        # ---------------------------------------------------------------------------------------------------------- #
        # Select the appropriate colormap for the image data
        add_to_legend = False
        if raster["mapping_style"] == "RGB":
            choosen_cmap = None
            add_to_legend = False
        elif raster["mapping_style"] == "trough_mapping":
            legend_color = (0.3, 0.3, 0.3, 0.75)
            choosen_cmap = ListedColormap([
                (0, 0, 0, 0),      # RGBA for 0: fully transparent
                (legend_color)  # RGBA for 1: gray with alpha=0.75
                ])
            add_to_legend = True
        else:
            raise ValueError("The provided colormap information in the image_background list does not seem to be valid. Please provide either a string for a built-in colormap, None for no colormap, or a tuple of RGBA values for a custom colormap.")
        # Add the image data to the plot with the specified interpolation method and z-order
        axes[tiff_axis[0]].imshow(
            img_data,
            extent = img_extent,
            origin = "upper",
            aspect = "equal",
            interpolation = "bilinear",
            zorder = z_order,
            cmap = choosen_cmap
            )
        if add_to_legend == True:
            axes[legend_axis[0]].fill_between([], [], color = legend_color, label = raster["label"])

        z_order += 1
    results = {}
    grouped_results = {}
    for value_col, plotting_info in plot_overlay.items():
        results["Mean " + plotting_info[0]] = []
        results["Std " + plotting_info[0]] = []
        if not "Description" in results.keys():
            results["Description"] = []

        print(" -------------------------------------------------------------------------------------------- ")
        print(f"Adding plot overlay for {value_col} with label {plotting_info} to the figure.")
        results["Description"] += ["Complete Subsidence Free Center"]
        results["Mean " + plotting_info[0]] += [gdf_only_center[value_col].mean()]
        results["Std " + plotting_info[0]] += [gdf_only_center[value_col].std()]

        results["Description"] += ["Identified Troughs of the Subsidence Free Center"]
        results["Mean " + plotting_info[0]] += [gdf_only_center.loc[(gdf_only_center["iwp_mapping_values"] == 1), value_col].mean()]
        results["Std " + plotting_info[0]] += [gdf_only_center.loc[(gdf_only_center["iwp_mapping_values"] == 1), value_col].std()]

        results["Description"] += ["Other Areas of the Subsidence Free Center"]
        results["Mean " + plotting_info[0]] += [gdf_only_center.loc[(gdf_only_center["iwp_mapping_values"] == 0), value_col].mean()]
        results["Std " + plotting_info[0]] += [gdf_only_center.loc[(gdf_only_center["iwp_mapping_values"] == 0), value_col].std()]

        results["Description"] += ["Complete Surrounding Area"]
        results["Mean " + plotting_info[0]] += [gdf_everything_else[value_col].mean()]
        results["Std " + plotting_info[0]] += [gdf_everything_else[value_col].std()]

        results["Description"] += ["Identified Troughs of the Surrounding Area"]
        results["Mean " + plotting_info[0]] += [gdf_everything_else.loc[(gdf_everything_else["iwp_mapping_values"] == 1), value_col].mean()]
        results["Std " + plotting_info[0]] += [gdf_everything_else.loc[(gdf_everything_else["iwp_mapping_values"] == 1), value_col].std()]

        results["Description"] += ["Other Areas of the Surrounding Area"]
        results["Mean " + plotting_info[0]] += [gdf_everything_else.loc[(gdf_everything_else["iwp_mapping_values"] == 0), value_col].mean()]
        results["Std " + plotting_info[0]] += [gdf_everything_else.loc[(gdf_everything_else["iwp_mapping_values"] == 0), value_col].std()]

        gdf.plot(
            ax = axes[tiff_axis[0]],
            column = value_col,
            zorder = z_order,
            legend = True,
            cmap = plotting_info[1],
            cax = axes[colorbar_axis[0]],
            legend_kwds = {"orientation": "horizontal"},
            linewidth = 4
            )
        z_order += 1
        axes[colorbar_axis[0]].set_title(plotting_info[0], pad = 10, fontsize = matplotlib_settings["legend.fontsize"])

    if not subtransect_rectangles == []:
        for box_number, box in enumerate(subtransect_rectangles, start=1):
            box_letter = chr(97 + box_number)
            # 1. Coordinates
            x1, y1 = box["easting_min"], box["northing_min"]
            x2, y2 = box["easting_max"], box["northing_max"]

            # 2. Calculate the Angle of the line between them
            dx = x2 - x1
            dy = y2 - y1
            angle = np.degrees(np.arctan2(dy, dx))

            # 3. Calculate the Width (distance between the points)
            width = np.sqrt(dx**2 + dy**2)

            # 4. Calculate a height/ thickness
            height = box.get("height", width * 0.5)
            rect = mpatches.Rectangle(
                (x1, y1),
                width,
                height,
                angle=angle,
                rotation_point="xy", # Rotate around the first corner
                fill=False,
                edgecolor=box.get("edgecolor", "red"),
                linewidth=box.get("linewidth", 2),
                linestyle=box.get("linestyle", "--"),
                zorder=z_order + 1,
                )
            axes[tiff_axis[0]].add_patch(rect)

            axes[tiff_axis[0]].text(
                box["x_text"],
                box["y_text"],
                f"({box_letter})",
                ha = "center",
                va = "center_baseline",
                fontsize = legend_fontsize,
                fontweight = "bold",
                color = box.get("text_color", "black"),
                bbox = dict(
                    facecolor = box.get("text_bg", "white"),
                    alpha = 0.7,
                    edgecolor = "none",
                    boxstyle = "round,pad=0.15",
                    ),
                zorder = z_order + 2,
                )
            axes[tiff_axis[0]].add_patch(rect)

    # Add transect points to the plot
    iwp_points.plot(
        ax = axes[tiff_axis[0]],
        color = "black",
        markersize = 20
        )
    for _, row in iwp_points.iterrows():
        text = row["study_site_id"][-1:]
        shift = 10
        if text == "1":
            xytext = (-shift, -shift)
        elif text == "2":
            xytext = (0, -shift)
        elif text == "3":
            xytext = (0, shift)
        elif text == "4":
            xytext = (shift, 0)
        elif text == "5":
            xytext = (0, shift)
        elif text == "6":
            xytext = (shift, 0)
        elif text == "7":
            xytext = (shift, 0)
        elif text == "8":
            xytext = (0, -shift)
        elif text == "9":
            xytext = (shift, 0)
        else:
            raise ValueError(f"{text} unknonw.")

        axes[tiff_axis[0]].annotate(
            text = text,
            xy = (row.geometry.x, row.geometry.y),
            xytext = xytext,
            textcoords = "offset points",
            fontweight = "bold",
            color = "black",
            ha = "center",
            va = "center_baseline",
            bbox = dict(
                facecolor = "white",
                edgecolor = "none",
                alpha = 0.7,
                boxstyle = "round,pad=0.15"
                ),
            )
    axes[legend_axis[0]].axis("off")  # Hide the axes for the legend
    axes[legend_axis[0]].legend(loc = "center", frameon = False)

    axes[spacer_axis_0[0]].axis("off")  # Hide the axes for the spacer
    axes[spacer_axis_1[0]].axis("off")  # Hide the axes for the spacer

    axes[tiff_axis[0]].set_xlabel("Easting (m)")
    axes[tiff_axis[0]].set_ylabel("Northing (m)")
    axes[tiff_axis[0]].ticklabel_format(useOffset = False, style = "plain", axis = "y")

    fig.canvas.draw()
    tiff_pos = axes[tiff_axis[0]].get_position()
    cax_pos = axes[colorbar_axis[0]].get_position()
    new_cax_pos = [
        tiff_pos.x0,      # Match the left edge
        cax_pos.y0,       # Keep original vertical position
        tiff_pos.width,   # Match the actual width of the image
        cax_pos.height    # Keep original colorbar height
        ]
    axes[colorbar_axis[0]].set_position(new_cax_pos)

    fig.canvas.draw()
    fig.suptitle(title, y = 0.93)
    fig.text(0.5, 0.885, f"Used EPSG:{wanted_epsg_crs} for spatial reference", ha = "center", va = "center")

    save_path.parent.mkdir(exist_ok=True)
    fig.savefig(save_path, dpi = dpi, bbox_inches = "tight", pad_inches = 0.05)
    plt.close(fig)

    return results, gdf_only_center, gdf_everything_else

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
