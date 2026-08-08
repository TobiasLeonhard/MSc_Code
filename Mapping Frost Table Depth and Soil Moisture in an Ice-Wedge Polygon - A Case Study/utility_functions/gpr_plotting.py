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
from config.environment import *
from utility_functions.combine_tifs import get_combined_raster
from utility_functions.gnss_handling import load_control_points
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def adjust_cut_width_based_on_transect_length(cut_half_width: float, data: gpd.GeoDataFrame, fig_width: float, height_unit_cm: float, height_ratios: list) -> float:
    """
    Adjusts the cut_half_width for cropping the orthomosaic based on the length of the transect and the allocated height for the orthomosaic subplot in the figure.
    This function ensures that the cropped orthomosaic fits well within the allocated height in the figure while maintaining an appropriate width to visualize the context around the transect.
    The function estimates the required height for the orthomosaic subplot based on the length of the transect and the current cut_half_width, and compares it to the allowed height for the subplot in the figure.
    If the estimated height exceeds the allowed height, the function reduces the cut_half_width proportionally to fit the orthomosaic within the allocated height.
    Args:
        cut_half_width - float: The initial half-width in meters for cropping the orthomosaic
        data - gpd.GeoDataFrame: The GeoDataFrame containing the transect data, used to determine the length of the transect.
        fig_width - float: The total width of the figure in inches, used to calculate the
        height_unit_cm - float: The height unit in centimeters, used to calculate the allowed height for the orthomosaic subplot based on the height ratios.
        height_ratios - list: List of height ratios for the subplots in the figure, used to calculate the allowed height for the orthomosaic subplot.
    Returns:
        new_cut_half_width - float: The adjusted half-width in meters for cropping the orthomosaic, which ensures that the subplot fits well within the allocated height in the figure.
    """
    # For some plots, we need to adjust the extent (cut_half_width_m) so that it fits width-wise
    # First we get the total height of the x-axis text in inches.
    inches_height_of_x_axis_text = (plt.rcParams["xtick.major.size"] + plt.rcParams["xtick.major.pad"] + plt.rcParams["axes.labelpad"] + 1.1 * (matplotlib_settings["font.size"] + matplotlib_settings["axes.labelsize"]))/ 72  # 72 points per inch

    range_x = data["distance_from_starting_pos_m"].max() - data["distance_from_starting_pos_m"].min()
    fig_unit_scale = fig_width / range_x

    estimated_sub_fig_height = (cut_half_width * 2) * fig_unit_scale + inches_height_of_x_axis_text # Respecting the height of the axis text
    allowed_sub_fig_height = height_unit_cm/2.54*height_ratios[-1] - inches_height_of_x_axis_text # Respecting the height of the axis text of the plot above
    if estimated_sub_fig_height > allowed_sub_fig_height - 0.2:
        old_cut_half_width = cut_half_width
        new_cut_half_width = cut_half_width * ((allowed_sub_fig_height - 0.2) / estimated_sub_fig_height)
        print(f"Adjusted cut_half_width from {old_cut_half_width:.2f} m to {new_cut_half_width:.2f} m to fit the orthomosaic subplot within the allocated height in the figure.")
    elif allowed_sub_fig_height > estimated_sub_fig_height + 0.3:
        old_cut_half_width = cut_half_width
        new_cut_half_width = cut_half_width * (allowed_sub_fig_height / (estimated_sub_fig_height + 0.3))
        print(f"Adjusted cut_half_width from {old_cut_half_width:.2f} m to {new_cut_half_width:.2f} m to better use the allocated height for the orthomosaic subplot in the figure.")
    else:
        new_cut_half_width = cut_half_width
    return new_cut_half_width

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_gpr_traces(ax: matplotlib.axes.Axes, transect_data: gpd.GeoDataFrame, trace_column: str, title: Union[str, None] = None, y_label: str = "Time (ns)", vel: Union[float, None] = None) -> matplotlib.axes.Axes:
    """
    Plots GPR traces on the provided matplotlib axis.

    Args:
        ax - matplotlib.axes.Axes: Axis to plot on.
        transect_data - gpd.GeoDataFrame: DataFrame containing GPR and GPS data.
        trace_column - str: Column name in transect_data containing trace values.
        title - str, optional: Title for the plot.
        y_label - str, optional: Label for the y-axis ("Time (ns)" or "Depth (cm)").
        vel - float, optional: Velocity in m/ns for depth conversion (if y_label is "Depth (cm)").
    Returns:
        matplotlib.axes.Axes: The axis with the plotted GPR traces.
    """
    data = np.array(transect_data[trace_column].tolist()).T
    clip = float(np.percentile(np.abs(data[~np.isnan(data)]), 99))
    start_extent = transect_data["distance_from_starting_pos_m"].iloc[0]
    end_extent = transect_data["distance_from_starting_pos_m"].iloc[-1]
    extent = (
        float(start_extent),
        float(end_extent),
        float((data.shape[0] - 1) * transect_data["dt_ns"].iloc[0]),
        0.0,
        )
    if clip is None:
        raise ValueError("Clip is None")
    ax.imshow(data,
              cmap = "gray",
              vmin = - clip,
              vmax = clip,
              aspect = "auto",
              origin = "upper",
              extent = extent
              )
    if y_label == "Time (ns)":
        ax.set_ylabel("Time (ns)")
    elif y_label == "Depth (m)":
        if vel is None:
            vel = 0.1  # default velocity if not provided
        ticks = ax.get_yticks()
        ylim = ax.get_ylim()
        # Only show ticks that are within the current y-limits -> Inverted axis so the sorting is reversed
        visible_xticks = [tick for tick in ticks if ylim[1] <= tick <= ylim[0]]
        ax.set_yticks(visible_xticks)
        ax.set_yticklabels([f"{tick * vel / 2:.1f}" for tick in visible_xticks])

        ax.set_ylabel("Depth (m) calculated using\n a velocity of {:.2f} m ns⁻¹".format(vel))
    if title:
        ax.set_title(title)
    return ax

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def add_enumaration_to_subplot(ax: matplotlib.axes.Axes, enumaration: str) -> matplotlib.axes.Axes:
    """
    Adds a text box at the left lower part of the subplot

    Args:
        ax - matplotlib.axes.Axes: Axis to add the text box to.
        enumaration - matplotlib.axes.Axes: Text to display in the enumeration box.

    Returns:
        ax -  matplotlib.axes.Axes: Axis with the added enumeration text box.
    """
    ax.text(
        0.02, 0.05, enumaration,
        transform = ax.transAxes,
        fontweight = "bold",
        va = "bottom",
        ha = "left",
        bbox = dict(facecolor = "white", alpha = 0.5, edgecolor = "none", boxstyle = "round,pad=0.2")
        )
    return ax

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def add_identification_to_plot(ax: matplotlib.axes.Axes, transect_data: gpd.GeoDataFrame, x_col: str, y_col: str, identification_col: str, alpha: float = 0.6, linewidth: float = 1.5, z_order: Union[int, None] = None) -> Tuple[matplotlib.axes.Axes, int]:
    """
    Adds scatter points to the GPR trace plot based on identification data.
    This can for example be used to highlight points identified as wet or dry areas.
    Args:
        ax - matplotlib.axes.Axes: Axis to plot on.
        transect_data - gpd.GeoDataFrame: DataFrame with GPR and GPS data.
        x_col - str: Column name for x-coordinates.
        y_col - str: Column name for y-coordinates.
        identification_col - str: Column name for identification data.
        alpha - float, optional: Transparency level for scatter points. Defaults to 0.6.
        linewidth - float, optional: Line width for the plot lines. Defaults to 1.5.
        use_volumetric_soil_moisture_classification - bool, optional: Whether to use new identification column. Defaults to False.
        z_order - int, optional: The z-order used for the scatter points. Defaults to np.nan.
    Returns:
        ax - matplotlib.axes.Axes: The axis with the added scatter points.
        z_order_out - int: The z-order used for the scatter points (can be used for further plotting to ensure correct layering).
        """
    for unique_id in transect_data[identification_col].unique():
        mask = transect_data[identification_col] == unique_id
        if identification_col == "is_hummock":
            if unique_id == True:
                color = "#924da7"
                label = "Identified as Hummock"
            elif unique_id == False:
                color = "black"
                label = "Identified as Interhummock"
        elif identification_col == "volumetric_soil_moisture_classification":
            if unique_id == "identified_as_wet":
                color = "blue"
                label = "Identified as Wet Area"
            elif unique_id == "identified_as_dry":
                color = "red"
                label = "Identified as Dry Area"
            elif unique_id == "identified_as_moist":
                color = "black"
                label = "Identified as Moist Area"
            else:
                color = "gray"
                label = "Other"
        x_vals = pd.to_numeric(transect_data[x_col], errors = "coerce").to_numpy(dtype = float)
        y_vals = transect_data[y_col].values
        masked_y = np.ma.masked_where(~mask, y_vals)
        if z_order is None:
            ax.plot(
                x_vals,
                masked_y,
                color = color,
                label = label,
                alpha = alpha,
                linewidth = linewidth,
                solid_capstyle = "butt"
                )
            z_order_out = 0
        else:
            ax.plot(
                x_vals,
                masked_y,
                color = color,
                label = label,
                alpha = alpha,
                linewidth = linewidth,
                zorder = z_order,
                solid_capstyle = "butt"
                )
            z_order_out = z_order + 1  # Increment z-order for the next set of points to ensure proper layering

    return ax, z_order_out

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_active_layer_on_gpr_trace(ax: matplotlib.axes.Axes, transect_data: gpd.GeoDataFrame, used_velocities_m_ns: dict) -> matplotlib.axes.Axes:
    """
    Plots the active layer thickness points on the GPR trace.
    Args:
        ax - matplotlib.axes.Axes: Axis to plot on.
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
        used_velocities_m_ns - dict: Dictionary of velocities used to convert active layer thickness from
    Returns:
        ax - matplotlib.axes.Axes: Axis to plot on.
    """
    for vel_key, used_velocity_info in used_velocities_m_ns.items():
        description = used_velocity_info[1]
        trace = []
        active_layer_thickness = []
        for _, row in transect_data.loc[transect_data[f"alt_for_{vel_key}_ns"].notna()].iterrows():
            trace.append(row["distance_from_starting_pos_m"])
            active_layer_thickness.append(row[f"alt_for_{vel_key}_ns"])
        if description == "no description":
            label_str = f"Measured Frozen Table Depth"
            ax.scatter(
                trace,
                active_layer_thickness,
                s=40,
                marker="o",
                facecolors="white",
                edgecolors="red",
                label=label_str,
                alpha=0.8,
                zorder=10
                )
        else:
            label_str = f"Active Layer Thickness ({description})"
            ax.scatter(
                trace,
                active_layer_thickness,
                s=30,
                marker="o",
                label=label_str,
                alpha=0.8,
                zorder=10
                )
    ax.legend(loc="lower right")
    return ax

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def adjust_x_tick_labels_and_grid(ax: matplotlib.axes.Axes, ticks_interval: float = np.nan) -> matplotlib.axes.Axes:
    """
    Adjusts the x-axis tick labels and grid based on the provided ticks interval.
    If ticks_interval is NaN, won't adjust the ticks and will keep the default ticks.
    Args:
        ax - mpl.axes.Axes: Axis to adjust.
        ticks_interval - float, optional: Interval for x-axis ticks. Defaults to np.nan.
    Returns:
        ax - mpl.axes.Axes: Adjusted axis.
    """
    if not np.isnan(ticks_interval):
        ax.xaxis.set_major_locator(ticker.MultipleLocator(ticks_interval))
    return ax

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_volumetric_soil_water_content(ax: matplotlib.axes.Axes, transect_data: gpd.GeoDataFrame, cmap_str: str = "viridis_r", baseline: float = 0.0) -> Tuple[matplotlib.axes.Axes, LineCollection]:
    """
    Plots the volumetric soil water content profile on the given axis.
    The volumetric soil water content is plotted on top of the elevation profile using a color (gradient) fill to visualize the variations in soil moisture along the transect.
    The plot includes a legend to indicate the meaning of the colors and a label for the y-axis.
    Args:
        ax - mpl.axes.Axes: Axis to plot on.
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
        cmap_str - str: The name of the colormap to use for plotting the volumetric soil water content.
        baseline - float: The baseline value for the fill (default is 0.0).
    Returns:
        ax - mpl.axes.Axes: Axis with the plotted volumetric soil water content profile.
        lc - LineCollection: The LineCollection object for the volumetric soil water content.
    """
    # Define the colormap for the volumetric soil water content
    cmap = plt.get_cmap(cmap_str)

    # Use 0 and 1 for comparison
    norm = Normalize(0, 1)

    # ------------------------------------------------------------------#
    # Plot the color fill with a gradient
    # ------------------------------------------------------------------#
    # To plot the gradient fill, we have to generate a polygon for each segment, therefore we need to prepare our data accordingly
    x = pd.to_numeric(transect_data["distance_from_starting_pos_m"], errors = "coerce").to_numpy(dtype=float)
    y_baseline = np.ones_like(x) * baseline
    y_calculated_depths = pd.to_numeric(transect_data["calculated_depths_m"], errors="coerce").to_numpy(dtype=float)

    # Create segments for the gradient -> vertical lines from the baseline to the calculated depth for each x value
    segments = [
        [[float(x[i]), float(y_baseline[i])], [float(x[i]), float(y_calculated_depths[i])]]
        for i in range(len(x))
        ]

    # Put the segments together in a LineCollection and set the colors based on the volumetric soil water content values and add to the plot
    lc = LineCollection(segments, cmap = cmap, norm = norm)
    lc.set_array(transect_data["volumetric_soil_water_content"].to_numpy(dtype=float))
    ax.add_collection(lc)

    return ax, lc

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_calculated_depth(ax: matplotlib.axes.Axes, transect_data: gpd.GeoDataFrame) -> matplotlib.axes.Axes:
    """
    Plots the calculated depth profile on the given axis and adds the active layer thickness points on top of it.
    Args:
        ax - mpl.axes.Axes: Axis to plot on.
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
    Returns:
        ax - mpl.axes.Axes: Axis with the plotted calculated depth profile.
    """
    highest_zorder = max(artist.zorder for artist in ax.get_children())
    ax.plot(transect_data["distance_from_starting_pos_m"], transect_data["calculated_depths_m"], color = "gray", linewidth=1.5, linestyle = "-", label="Calculated Frozen Table Depth", zorder=highest_zorder + 1)
    mask = transect_data["active_layer_thickness_m"].notna()
    ax.scatter(transect_data.loc[mask, "distance_from_starting_pos_m"], transect_data.loc[mask, "active_layer_thickness_m"], facecolors="none", edgecolors="red", marker="o", s=40, label="Measured Frozen Table Depth", zorder=highest_zorder + 2)
    # Adjust limits and labels
    ax.set_ylabel("Depth to\nFrozen Table (m)")
    ax.set_xlabel("")
    ax.set_xlim(transect_data["distance_from_starting_pos_m"].min(), transect_data["distance_from_starting_pos_m"].max())
    ax.set_ylim(0, transect_data["calculated_depths_m"].max() + np.absolute((transect_data["calculated_depths_m"].dropna().min() - transect_data["calculated_depths_m"].dropna().max()))/100*2)
    ax.legend(loc="lower right")
    ax.invert_yaxis()
    return ax

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_elevation_profile_and_active_layer_thickness(ax: matplotlib.axes.Axes, transect_data: gpd.GeoDataFrame, dist_val: str = "distance_from_starting_pos_m", elev_val: str = "elevation_m", y_label: str = "Surface Elevation\n from Sea Level (m)", x_label: str = "Distance from start of transect (m)", alt_val: str = "calculated_depths_m") -> matplotlib.axes.Axes:
    """
    Plots the elevation profile on the given axis.
    Args:
        ax - mpl.axes.Axes: Axis to plot on.
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
        dist_val - str, optional: Column name for distance values. Defaults to "distance_from_starting_pos_m".
        elev_val - str, optional: Column name for elevation values. Defaults to "elevation_corrected_by_rtk_m".
        y_label - str, optional: Label for the y-axis. Defaults to "Surface Elevation\n from Sea Level (m)".
        x_label - str, optional: Label for the x-axis. Defaults to "Distance from start of transect (m)".
        alt_val - str, optional: Column name for active layer thickness values. Defaults to "active_layer_thickness_m".
    Returns:
        ax - mpl.axes.Axes: Axis with the plotted elevation profile.
    """
    ax.plot(transect_data[dist_val], transect_data[elev_val], "b-", label="Surface Elevation")
    ax.fill_between(transect_data[dist_val], transect_data[elev_val], transect_data[elev_val] - transect_data[alt_val], color="lightblue", alpha=0.5, label="Thawed Layer")
    min_depth = (transect_data[elev_val] - transect_data[alt_val]).min() - 0.5
    # Catching cases where the min depth is NaN and adjusting the value.
    if np.isnan(min_depth):
        min_depth = transect_data[elev_val].max() - 2
    ax.fill_between(transect_data[dist_val], transect_data[elev_val] - transect_data[alt_val], min_depth, color="gray", alpha=0.5, label="Frozen Layer")
    ax.set_ylabel(y_label)
    ax.set_xlim(transect_data[dist_val].min(), transect_data[dist_val].max())
    ax.set_xlabel(x_label)
    ax.set_ylim(min_depth, transect_data[elev_val].max() + 0.25)
    ax.legend(loc="lower right")
    return ax

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def add_trace(axis: matplotlib.axes.Axes, data: gpd.GeoDataFrame, x_col: str, y_col: str, tick_col: str, ticks: list, label: str, color: str, linestyle: str, markersize: int, alpha: float, z_order: int, y_range: float) -> Tuple[matplotlib.axes.Axes, int]:
    """
    This function adds a trace using the x_col and y_col from the data GeoDataFrame to the provided axis.
    It also adds scatter points at the specified ticks, depending on the tick_col in the data GeoDataFrame and the provided ticks list.
    The trace is plotted with the specified label, color, linestyle, markersize, alpha, and z_order.
    Args:
        axis - matplotlib.axes.Axes: Axis to plot on.
        data - gpd.GeoDataFrame: DataFrame containing the data to plot.
        x_col - str: Column name for the x-axis values.
        y_col - str: Column name for the y-axis values.
        tick_col - str: Column name for the tick values.
        ticks - list: List of tick values to plot scatter points for.
        label - str: Label for the trace.
        color - str: Color for the trace.
        linestyle - str: Linestyle for the trace.
        markersize - int: Size of the scatter points.
        alpha - float: Alpha value for the trace.
        z_order - int: Z-order for the trace.
        y_range - float: Range of the y-axis values.
    Returns:
        axis - matplotlib.axes.Axes: The axis with the added trace and scatter points.
        z_order - int: The z-order used for the trace (can be used for further plotting to ensure correct layering).
    """
    axis.plot(data[x_col], data[y_col], label = label, color = color, linestyle = linestyle, alpha = alpha, zorder = z_order)

    # Calculate y-offset for the scatter points based on the y_range to ensure they are visible above the trace
    y_offset = 0.05 * np.abs(y_range)  # Adjust the multiplier as needed for better visibility
    # Sort the data frame and extract the rows corresponding to the specified ticks for scatter points
    df = data.sort_values(tick_col).copy()
    tick_df = pd.DataFrame({"ticks": sorted(ticks)})
    extracted_data = pd.merge_asof(
        tick_df,
        df,
        left_on = "ticks",
        right_on = tick_col,
        direction = "nearest"
        )
    axis.scatter(extracted_data[x_col], extracted_data[y_col], marker = 2, color = "black", s = 50)
    for i in range(len(extracted_data)):
        # Round the value
        tick_value = np.round(extracted_data[tick_col].iloc[i], decimals=0)

        # Add text with a white alpha background (bbox)
        axis.text(
            extracted_data[x_col].iloc[i],
            extracted_data[y_col].iloc[i] + y_offset,
            f"{int(tick_value)}",
            ha = "center",
            va = "bottom",
            bbox = dict(
                facecolor = "white",
                alpha = 0.5,
                edgecolor = "none",
                boxstyle = "round,pad=0.1",
                mutation_scale = 1
                )
            )
    z_order += 1  # Increment z-order for the next plot to ensure proper layering
    return axis, z_order

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_tif_background_with_gpr_trace(ax: matplotlib.axes.Axes, ax_ticks: matplotlib.axes.Axes, transect_data_for_plotting: dict, transect_data: gpd.GeoDataFrame, use_rasters: List[str], y_margin: float, add_active_layer: bool, identification_col: str, identification_alpha: float = 1) -> matplotlib.axes.Axes:
    """
    Plots the orthomosaic image with the GPR trace and optionally active layer points.

    Args:
        ax - matplotlib.axes.Axes: Axis to plot on.
        ax_ticks - matplotlib.axis.XAxis: Axis that is used to adjust the x ticks
        transect_data_for_rgb_plot - dict: Dictionary containing RGB image and image extent.
        transect_data - gpd.GeoDataFrame: DataFrame with GPR and GPS data.
        use_rasters - List[str]: List of raster names to use for the background.
        y_margin - float: Margin to add to y-axis limits (meters).
        add_active_layer - bool: Whether to plot active layer points.
        height_ratio - float: Height ratio for the plot aspect.
        height - float: Height of the plot in inches.
        identification_alpha - float: Alpha value for the identification coloring (between 0 and 1).
    Returns:
        matplotlib.axes.Axes: The axis with the plotted orthomosaic and traces.
    """
    # Check if transect relative GPS coordinates are available and sufficient for plotting
    if transect_data["transect_relative_x_gps_coordinate_m"] is None or len(transect_data["transect_relative_x_gps_coordinate_m"]) <= 1:
        raise ValueError("GPS coordinates are not available or insufficient for plotting. Cannot plot orthomosaic background with GPR trace.")
    if transect_data["transect_relative_y_gps_coordinate_m"] is None or len(transect_data["transect_relative_y_gps_coordinate_m"]) <= 1:
        raise ValueError("GPS coordinates are not available or insufficient for plotting. Cannot plot orthomosaic background with GPR trace.")

    # Get x-axis limits based on GPS coordinates and add margin
    x_min = min(transect_data["transect_relative_x_gps_coordinate_m"].min(), transect_data["transect_relative_x_gps_coordinate_m"].min())
    x_max = max(transect_data["transect_relative_x_gps_coordinate_m"].max(), transect_data["transect_relative_x_gps_coordinate_m"].max())
    ymin = transect_data["transect_relative_y_gps_coordinate_m"].min() - y_margin
    ymax = transect_data["transect_relative_y_gps_coordinate_m"].max() + y_margin
    y_range = ymax - ymin
    # Set the zorder to 0 to ensure the image is in the background
    z_order = 0
    # Add the tif image as listed in the tif_bands list to the background of the plot using the extent from the cut out area around the transect
    for raster in use_rasters:
        mapping_style = transect_data_for_plotting[raster]["mapping_style"]
        image_data = transect_data_for_plotting[raster]["img_data"]
        label = transect_data_for_plotting[raster]["label"]
        if mapping_style == "RGB":
            cmap = None
            legend_color = None
        elif mapping_style == "trough_mapping":
            legend_color = (0.3, 0.3, 0.3, 0.75)
            cmap = ListedColormap([
                (0, 0, 0, 0),      # RGBA for 0: fully transparent
                (legend_color)  # RGBA for 1: gray with alpha=0.75
                ])
            # Round the image data to 0 and 1 and convert to int for the colormap
            image_data = np.round(image_data).astype(int)
        elif mapping_style == "hummock_mapping":
            legend_color = (0.3, 0.3, 0.3, 0.75)
            cmap = ListedColormap([
                (0, 0, 0, 0),      # RGBA for 0: fully transparent
                (legend_color)  # RGBA for 1: gray with alpha=0.75
                ])
            # Round the image data to 0 and 1 and convert to int for the colormap
            image_data = np.round(image_data).astype(int)
        else:
            raise ValueError(f"Mapping style {mapping_style} not recognized, please add support for it.")

        ax.imshow(
            image_data,
            extent = transect_data_for_plotting["rotational_info"]["rotated_full_extent"],
            origin = "upper",
            aspect = "equal",
            interpolation = "bilinear",
            cmap = cmap,
            zorder = z_order
            )

        if label is not None:
            ax.fill_between([], [], color = legend_color, label = label)  # Add invisible fill for legend entry

        z_order += 1  # Increment z_order for the next band to ensure proper layering

    # Add the GPR trace with the identification coloring on top of the image

    ax, z_order = add_identification_to_plot(
        ax,
        transect_data,
        "transect_relative_x_gps_coordinate_m",
        "transect_relative_y_gps_coordinate_m",
        identification_col = identification_col,
        linewidth=5,
        z_order = z_order,
        alpha = identification_alpha,
        )

    # Get current ticks
    x_ticks = ax_ticks.get_xticks()
    x_ticks_lim = ax_ticks.get_xlim()

    # Only show ticks that are within the current x-limits
    visible_x_ticks = [tick for tick in x_ticks if x_ticks_lim[0] <= tick <= x_ticks_lim[1]]

    ax, z_order = add_trace(
        axis = ax,
        data = transect_data,
        x_col = "transect_relative_x_gps_coordinate_m",
        y_col = "transect_relative_y_gps_coordinate_m",
        tick_col = "distance_from_starting_pos_m",
        ticks = visible_x_ticks,
        label = "GPR Trace from GPS",
        color = "gray",
        linestyle = "-.",
        markersize = 7,
        alpha = 0.8,
        z_order = z_order,
        y_range = y_range
        )


    if add_active_layer:
        active_layer_mask = ~transect_data["active_layer_thickness_m"].isna()
        # Plot active layer points
        ax.scatter(
            x = transect_data["alt_data_transect_relative_x"][active_layer_mask],
            y = transect_data["alt_data_transect_relative_y"][active_layer_mask],
            c = "yellow",
            s = 30,
            marker = "o",
            label = "Frozen Table Probing Location",
            alpha = 0.8,
            zorder = z_order)
        z_order += 1  # Increment z_order for the next elements to ensure proper layering

    # ------------------------------------------------------------------------------
    # ---------------------------------------
    # Set limits
    # ---------------------------------------
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(x_min, x_max)

    # ------------------------------------------------------------------------------
    # ---------------------------------------
    # Set labels
    # ---------------------------------------
    ax.set_xlabel("Distance along transect-centered axis (m)")
    ax.set_ylabel("Distance perpendicular\nto transect (m)")

    ax.legend()

    return ax

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def handle_legend_entrances(axes: List[matplotlib.axes.Axes], axis: matplotlib.axes.Axes, legend_order: list) -> matplotlib.axes.Axes:
    """
    Handles the legend entrances.

    Args:
        axes - List[matplotlib.axes.Axes]: List of Axes
        axis - matplotlib.axes.Axes: Axis where the legend is plotted
        legend_order - dict: Desired order for the legend entrances

    Returns:
        axis - matplotlib.axes.Axes: Axis where the legend is plotted
    """

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

    # Add empty spaces to extent the legend space
    max_col_len = max(len(col) for col in legend_order)
    empty_space_cnt = 0
    for col in legend_order:
        col_len = len(col)
        if col_len < max_col_len:
            empty_space_cnt += max_col_len - col_len
            col.extend([" " * (i+1) for i in range(max_col_len - col_len)])
    add_empty_rows = 3
    for col in legend_order:
        col.extend([" " * (empty_space_cnt + i + 1) for i in range(add_empty_rows)])
        empty_space_cnt += add_empty_rows
    desired_order = [item for sublist in legend_order for item in sublist]
    # Filter desired_order to include only keys that exist in by_label
    if "Identified as Wet Area" not in by_label:
        index = desired_order.index("Identified as Wet Area")
        desired_order[index] = "   "
    if "Identified as Moist Area" not in by_label:
        index = desired_order.index("Identified as Moist Area")
        desired_order[index] = "    "
    if "Identified as Dry Area" not in by_label:
        index = desired_order.index("Identified as Dry Area")
        desired_order[index] = "     "

    ordered_by_label = by_label.copy()
    # Create an ordered dictionary based on the desired order, filling in missing keys with a dummy entry
    for key in desired_order:
        if key not in ordered_by_label:
            ordered_by_label[key] = Line2D([], [], color = "none")
    ordered_by_label = {key: ordered_by_label[key] for key in desired_order}
    axis.legend(ordered_by_label.values(), ordered_by_label.keys(), loc="upper center", ncol=4)
    return axis

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def provide_title_from_sgy_path(pck_file: Path, gdf: gpd.GeoDataFrame, gpr_date: Union[str, None] = None) -> tuple[str, list]:
    """
    Provides a descriptive title for the GPR trace figure as well as individual components based on the SEG-Y file path.

    Args:
        pck_file - Path: Path to the SEG-Y file
        gdf - gpd.GeoDataFrame: Data Frame containing GPR information.
        gpr_date - str: Date of the GPR survey. Defaults to None

    Returns:
        overall_title - str: Descriptive title for the GPR trace figure
        [season_str, site_str, transect_num, frequency_str] - list: List of individual components
    """
    is_cropped = gdf["transect_cropped"].unique().item()
    if pck_file.stem.startswith("S"):
        season_str = "Summer"
    elif pck_file.stem.startswith("W"):
        season_str = "Winter"
    else:
        season_str = "Unknown Season"

    if "IWP" in pck_file.stem.upper():
        site_str = "IWP"
    elif "SIKSIK-LOWER" in pck_file.stem.upper():
        site_str = "Siksik-Lower"
    elif "SIKSIK-MIDDLE" in pck_file.stem.upper():
        site_str = "Siksik-Middle"
    elif "SIKSIK-UPPER" in pck_file.stem.upper():
        site_str = "Siksik-Upper"
    else:
        site_str = "Unknown Site"

    if site_str == "IWP":
        if "1-2" in pck_file.stem:
            transect_num = "1-2"
        elif "2-3" in pck_file.stem:
            transect_num = "2-3"
        elif "3-4" in pck_file.stem:
            transect_num = "3-4"
        elif "4-5" in pck_file.stem:
            transect_num = "4-5"
        elif "5-6" in pck_file.stem:
            transect_num = "5-6"
        elif "6-7" in pck_file.stem:
            transect_num = "6-7"
        elif "7-8" in pck_file.stem:
            transect_num = "7-8"
        elif "8-9" in pck_file.stem:
            transect_num = "8-9"
        elif "9-1" in pck_file.stem:
            transect_num = "9-1"
        else:
            transect_num = "Unknown-Transect"
        if "S-E" in pck_file.stem.upper():
            transect_num = transect_num
        elif "E-S" in pck_file.stem.upper():
            transect_num = transect_num[2] + transect_num[1]  + transect_num[0]
        else:
            transect_num = "Unknown-Transect"

    elif "Siksik-Lower" in site_str or "Siksik-Middle" in site_str or "Siksik-Upper" in site_str:
        if "-1_" in pck_file.stem:
            transect_num = "1"
        elif "-2_" in pck_file.stem:
            transect_num = "2"
        elif "-3_" in pck_file.stem:
            transect_num = "3"
        elif "-4_" in pck_file.stem:
            transect_num = "4"
        elif "-5_" in pck_file.stem:
            transect_num = "5"
        elif "-6_" in pck_file.stem:
            transect_num = "6"
        elif "-7_" in pck_file.stem:
            transect_num = "7"
        elif "-8_" in pck_file.stem:
            transect_num = "8"
        elif "-9_" in pck_file.stem:
            transect_num = "9"
        else:
            transect_num = "Unknown-Transect"
    else:
        transect_num = "Unknown-Transect"

    if "500MHZ" in pck_file.stem.upper():
        frequency_str = "500 MHz"
    elif "1GHZ" in pck_file.stem.upper() or "1000MHZ" in pck_file.stem.upper():
        frequency_str = "1 GHz"
    else:
        frequency_str = "Unknown Frequency"

    if is_cropped == False:
        overall_title = f"GPR Transect: {transect_num} | Site: {site_str} | Season: {season_str} | Frequency: {frequency_str}"
    else:
        overall_title = f"GPR Transect: {transect_num} (crp) | Site: {site_str} | Season: {season_str} | Frequency: {frequency_str}"

    if gpr_date is not None:
        overall_title += f" | Date: {gpr_date}"

    return overall_title, [season_str, site_str, transect_num, frequency_str]

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def convert_geometry_to_x_y_coordinates(transect_data: gpd.GeoDataFrame, geometry_col: str, new_col_subst: str) -> gpd.GeoDataFrame:
    """
    Converts a geometry column in the GeoDataFrame to separate x and y coordinate columns, making it ready for export.
    Args:
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with combined GPR and GPS data
        geometry_col - str: Column name in transect_data containing geometry data
        new_col_subst - str: Substring to replace in the geometry column name for the new x and y coordinate columns
    Returns:
        transect_data - gpd.GeoDataFrame: Geospatial dataframe with added x and y coordinate columns
    """
    if geometry_col in transect_data.columns:
        transect_data["x_coords_" + new_col_subst] = np.nan
        transect_data["y_coords_" + new_col_subst] = np.nan
        for idx, row in transect_data[transect_data[geometry_col].notna()].iterrows():
            transect_data.at[idx, "x_coords_" + new_col_subst] = row[geometry_col].x
            transect_data.at[idx, "y_coords_" + new_col_subst] = row[geometry_col].y
        transect_data = transect_data.drop(columns=[geometry_col])
    return transect_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def save_transect_data_to_parquet(data: gpd.GeoDataFrame, path: Path, geometry_cols: list[tuple[str, str]]) -> None:
    """
    Helper function that saves the transect data to a parquet file.
    The function transforms the geometry columns into x and y coordinate columns before saving, as parquet files do not support geometry data types.
    The saved parquet file will be stored in the "Transect Data Sets" folder, which is created if it does not exist, and will have the same name as the save_path with a .parquet extension.
    Args:
        data - gpd.GeoDataFrame: GeoDataFrame containing the transect data to be saved.
        path - Path: Path where the parquet file should be saved. The name of the parquet file will be derived from this path.
        geometry_cols - list: List of column names in the transect_data GeoDataFrame that contain geometry data and need to be transformed into x and y coordinate columns before saving.
    """
    # Columns stored in geometry_cols
    for col, new_col_substring in geometry_cols:
        if col in data.columns:
            data = convert_geometry_to_x_y_coordinates(data, col, new_col_substring)
    # Save to parquet
    data.to_parquet(path.with_suffix(".parquet"))
    data.to_file(path.with_suffix(".gpkg"), driver="GPKG")

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
def points_to_segments(gdf: gpd.GeoDataFrame, value_cols: list, sort_cols: list, smoothing_window: int = 5) -> gpd.GeoDataFrame:
    """
    Transforms points to a line style geometry with optional smoothing to prevent crisscrossing.

    Args:
        gdf- gpd.GeoDataFrame: Input GeoDataFrame.
        value_cols - list: Columns to average for segments.
        sort_cols - list: Columns to sort by (e.g., ['transect_id', 'distance']).
        smoothing_window - int: Number of points to average for coordinate smoothing. 1 = no smoothing.
    Returns:
        gdf - gpd.GeoDataFrame: GeoDataFrame with LineString geometries representing segments between points, and averaged values for specified columns.
    """
    # Ensure data is sorted
    gdf = gdf.sort_values(by=sort_cols).copy()

    # --- SMOOTHING STEP ---
    # We smooth the X and Y coordinates independently to reduce jitter
    # If your GDF has multiple transects, we should smooth within each group
    if smoothing_window > 1:
        # Identify the grouping column (usually the first sort_col, e.g., 'transect_name')
        group_col = sort_cols[0]

        # Smooth coordinates
        gdf["smooth_x"] = gdf.geometry.x.groupby(gdf[group_col]).transform(
            lambda x: x.rolling(window = smoothing_window, center = True, min_periods = 1).mean()
        )
        gdf["smooth_y"] = gdf.geometry.y.groupby(gdf[group_col]).transform(
            lambda x: x.rolling(window = smoothing_window, center = True, min_periods = 1).mean()
        )
        # Update geometry with smoothed points
        gdf.geometry = gpd.points_from_xy(gdf.smooth_x, gdf.smooth_y)

    segments = []

    # Iterate through groups (transects) to ensure we don't connect the end of one transect to the start of another
    group_col = sort_cols[0]
    for _, group in gdf.groupby(group_col):
        group = group.reset_index(drop=True)

        for i in range(len(group) - 1):
            p1 = group.geometry.iloc[i]
            p2 = group.geometry.iloc[i+1]

            # Avoid zero-length lines if points are identical after smoothing and check for nans
            if p1.equals(p2):
                continue
            if p1 is None or p2 is None or p1.is_empty or p2.is_empty:
                continue
            # Check specifically for NaN coordinates
            if np.isnan(p1.x) or np.isnan(p1.y) or np.isnan(p2.x) or np.isnan(p2.y):
                continue

            line = LineString([p1, p2])

            segment_data = {"geometry": line}
            for col in value_cols:
                # Average the value for the segment
                val = (group[col].iloc[i] + group[col].iloc[i+1]) / 2
                segment_data[col] = val

            segments.append(segment_data)

    return gpd.GeoDataFrame(segments, crs = gdf.crs)

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
