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

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2026
Last Modified: 2026-08-06
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
from utility_functions.gpr_plotting import adjust_cut_width_based_on_transect_length, plot_gpr_traces, add_identification_to_plot, adjust_x_tick_labels_and_grid, add_enumaration_to_subplot, plot_tif_background_with_gpr_trace, provide_title_from_sgy_path, save_transect_data_to_parquet
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def plot_hummock_detection_transect(transect_data: gpd.GeoDataFrame, image_data: dict, pck_file: Path, cut_half_width_m: float = 10.0, fig_width_cm: float = 30, height_unit_cm: float = 7.5, dpi: int = 300) -> None:
    """
    Plots hummock detection results transect wise.

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
    legend_axis = [0, 0.3]
    radiogram_axis_0 = [1, 0.9]
    tiff_axis = [2, 1.3]

    height_ratios = [
        legend_axis[1],
        radiogram_axis_0[1],
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

    # 1. Plot legend_axis -> Turn it off.
    axes[legend_axis[0]].axis("off")

    # 2. Plot radiogram_axis_0: GPR traces with ground selection and active layer thickness points
    axes[radiogram_axis_0[0]] = plot_gpr_traces(
        ax = axes[radiogram_axis_0[0]],
        transect_data = transect_data,
        trace_column = "trace_values",
        title = None,
        y_label = "Depth (m)"
        )
    axes[radiogram_axis_0[0]], _ = add_identification_to_plot(
        ax = axes[radiogram_axis_0[0]],
        transect_data = transect_data,
        x_col = "distance_from_starting_pos_m",
        y_col = "refl_line_travel_times_ns",
        linewidth = 5,
        identification_col = "is_hummock",
        alpha = 0.8
        )
    # Adjust x-tick labels and grid
    axes[radiogram_axis_0[0]] = adjust_x_tick_labels_and_grid(
        ax = axes[radiogram_axis_0[0]],
        ticks_interval = 10
        )
    axes[radiogram_axis_0[0]] = add_enumaration_to_subplot(
        ax = axes[radiogram_axis_0[0]],
        enumaration = "(a)"
        )
    axes[radiogram_axis_0[0]].set_xlabel("Distance from starting position (m)")

    # 3. Plot tiff_axis: Orthomosaic with GPS trace and active layer points
    axes[tiff_axis[0]] = plot_tif_background_with_gpr_trace(
        ax = axes[tiff_axis[0]],
        ax_ticks = axes[radiogram_axis_0[0]],
        transect_data_for_plotting = image_data,
        transect_data = transect_data,
        use_rasters = ["aerial_map", "hummock_map"],
        y_margin = updated_cut_half_width_m,
        add_active_layer = False,
        identification_alpha = 0.8,
        identification_col = "is_hummock"
        )
    axes[tiff_axis[0]] = add_enumaration_to_subplot(
        ax = axes[tiff_axis[0]],
         enumaration = "(b)"
         )

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
    axes[legend_axis[0]].legend(by_label.values(), by_label.keys(), loc='lower center', ncol=4)
    fig.canvas.draw()  # Redraw to update legend
    # -------------------------------------------------------------------#
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
    plt.subplots_adjust(
        left = 0.08,
        right = 0.98,
        top = 0.96,
        bottom = 0.08
        )

    save_path = results_folder / "gpr_analysis" / pck_file.stem
    save_path.parent.mkdir(parents = True, exist_ok = True)
    fig.savefig(
        save_path.with_suffix(".png"),
        dpi = dpi,
        bbox_inches = "tight",
        pad_inches = 0.2
        )

    # Close the figure to free memory
    plt.close(fig)

    # ----------------------------------------------------------------------------------------------- #
    # Save the transect data with all added information to a parquet file for future use
    geometry_cols = [("geometry_from_active_layer_data", "active_layer_data")]
    save_transect_data_to_parquet(
        data = transect_data,
        path = save_path,
        geometry_cols = geometry_cols
        )

    return None
