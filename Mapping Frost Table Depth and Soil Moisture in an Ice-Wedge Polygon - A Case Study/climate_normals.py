#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
climate_normals.py

This file contains functions for handling the climate normals.

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
parent_folder = Path(__file__).resolve().parent
sys.path.append(str(parent_folder))
from config.environment import *
from utility_functions.climate_normals import flatten_columns, rename_monthly_columns, load_tvc_gap_filled_data
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("climate_normals.py started")
    # Define output file name
    output_filename = results_folder / "climate_normals" / Path("TVC_climate_normals").with_suffix(".png")
    output_filename.parent.mkdir(exist_ok = True)

    # Define plotting colors
    temp_color = "tab:red"
    precipitation_color = "tab:blue"

    # Load data
    climate_data = load_tvc_gap_filled_data()
    # Remove whitespace
    climate_data.columns = climate_data.columns.str.strip()
    # Enforce every column to be numerical
    climate_data = climate_data.astype(float)
    # Check for existing columns
    cols_to_check = ["Year", "Month", "Day", "Hour", "Tair", "Snowfall", "Rainfall"]
    # Returns True only if ALL are present
    is_present = set(cols_to_check).issubset(climate_data.columns)
    if is_present == False:
        missing_cols = set(cols_to_check) - set(climate_data.columns)
        raise ValueError(f"Could not find the following columns: {missing_cols}")
    # Add Date column
    climate_data["Date"] = pd.to_datetime(
        pd.DataFrame({
            "year": climate_data["Year"],
            "month": climate_data["Month"],
            "day": climate_data["Day"],
            "hour": climate_data["Hour"]
                }
            )
        )
    # Select climate normal subset
    climate_data = climate_data[climate_data["Date"].between("1991-09-01 00:00", "2020-08-31 23:59:59")]
    # Convert Tair from Kelvin to Celsius
    climate_data["Tair"] = climate_data["Tair"] - 273.15
    # Add precipitations together and convert from kg/m²/s to mm/hr
    climate_data["Precipitation"] = climate_data["Snowfall"] + climate_data["Rainfall"]
    climate_data["Precipitation"] = climate_data["Precipitation"] * 3600

    # Group on daily basis and flatten the column
    climate_data_grp_daily = climate_data.set_index("Date").resample("D").agg(
        {
            "Tair": ["mean", "min", "max"],
            "Precipitation": ["sum"]
            }
        ).reset_index()
    climate_data_grp_daily = flatten_columns(
        df = climate_data_grp_daily,
        column_fill = "daily"
        )

    # Now group the flatten daily group on monthly basis and flatten the column
    climate_data_grp_monthly = climate_data_grp_daily.set_index("Date").resample("ME").agg(
        {
            "Tair_daily_mean": ["mean"],
            "Tair_daily_min": ["mean", "min"],
            "Tair_daily_max": ["mean", "max"],
            "Precipitation_daily_sum": ["sum"]
            }
        ).reset_index()
    climate_data_grp_monthly = flatten_columns(
        df = climate_data_grp_monthly,
        column_fill = "monthly"
        )

    # Rename the columns for easier handling and drop unwanted
    new_cols = [rename_monthly_columns(c) for c in climate_data_grp_monthly.columns]
    keep_cols = [c for c in new_cols if c is not None]
    climate_data_grp_monthly = climate_data_grp_monthly.loc[:, [c for c, nc in zip(climate_data_grp_monthly.columns, new_cols) if nc is not None]]
    climate_data_grp_monthly.columns = keep_cols

    # Group by month and calculate mean for each column
    climate_data_grp_monthly["Month"] = climate_data_grp_monthly["Date"].dt.month
    climate_normals = climate_data_grp_monthly.groupby("Month").mean(numeric_only=True).reset_index()

    # Plot climate normals: temperature (mean, min, max) and precipitation by month
    months = [calendar.month_abbr[m] for m in climate_normals["Month"]]
    fig, ax1 = plt.subplots(figsize=(10, 6))

    month_index = range(len(months))
    # Add temperature lines and temperature envelope
    ax1.fill_between(
        months,
        climate_normals["Tair_monthly_min"],
        climate_normals["Tair_monthly_max"],
        color = temp_color,
        alpha = 0.2,
        label = "Temperature Range (Min-Max)"
        )

    # Add mean temperature line
    ax1.plot(
        months,
        climate_normals["Tair_monthly_mean"],
        label = "Mean Temperature (°C)",
        color = temp_color,
        marker = "o"
        )

    # Add precipitation bar on right y-axis
    ax2 = ax1.twinx()
    ax2.bar(
        months,
        climate_normals["Precipitation_monthly_sum"],
        label = "Precipitation (mm)",
        color = precipitation_color,
        alpha = 0.3
        )

    # Handle axis labels, legend, title and layout
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Temperature (°C)", color = temp_color)
    ax2.set_ylabel("Precipitation (mm)", color = precipitation_color)
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left")
    plt.title("Climate Normals (1991-2020) - Trail Valley Creek")
    plt.tight_layout()

    # Save and close file
    plt.savefig(output_filename, dpi = DPI)
    plt.close()

    print("Climate normals saved successfully.")
    print(f"Maximal monthly mean temperature: {climate_normals['Tair_monthly_mean'].max()}°C.")
    print(f"Mean monthly mean temperature: {climate_normals['Tair_monthly_mean'].mean()}°C.")
    print(f"Minimal monthly mean temperature: {climate_normals['Tair_monthly_mean'].min()}°C.")
    print(f"Maximal monthly summed precipitaiton: {climate_normals['Precipitation_monthly_sum'].max()}°C.")
    print(f"Mean monthly summed precipitaiton: {climate_normals['Precipitation_monthly_sum'].mean()}°C.")
    print(f"Minimal monthly summed precipitaiton: {climate_normals['Precipitation_monthly_sum'].min()}°C.")
    print("\nclimate_normals.py finished.")
    print("# ====================================================================================================================================================== #")
