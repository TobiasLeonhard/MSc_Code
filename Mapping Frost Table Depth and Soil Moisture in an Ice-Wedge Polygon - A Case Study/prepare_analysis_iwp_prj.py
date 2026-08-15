#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
prepare_analysis_iwp_prj.py

Description:
This script organizes project data by copying input files from downloaded repositories to their designated project directories.
It manages meteorological data, aerial imagery, LiDAR products, field measurements, nine GPR survey transects with radargrams and reflection pick lines, and utility functions, ensuring the correct file structure for downstream ice-wedge polygon analysis workflows.
This setup script enables reproducible project initialization and data staging.

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
import shutil
parent_folder = Path(__file__).resolve().parent
sys.path.append(str(parent_folder))
from config.environment_iwp_prj import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("# ====================================================================================================================================================== #")
    print("prepare_analysis_hum_prj.py started")

    # Target perparation
    # Structure: "Label": [Source Folders], "Source File", "Dest Folder", "Dest Name"
    # Some files are not available for download yet, this will be corrected in future versions. These files are marked with "TBD" = True
    targets = {
    # Meterological data
        "meteorological data": {
            "folders": ["doi-10.5683-sp3-bxv4de", "meteorological data"],
            "src": "TVC_Gapfilled_Met_1991-2023.xlsx",
            "dst_dir": data_folder / "tvc_data" / "meteorology",
            "dst_name": "TVC_Gapfilled_Met_1991-2023.xlsx",
            "TBD": False
            },
        "meteorological data info": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "TVC_Gapfilled_Met_1991-2023.txt",
            "dst_dir": data_folder / "tvc_data" / "meteorology",
            "dst_name": "TVC_Gapfilled_Met_1991-2023.txt",
            "TBD": True
            },
    # Drone-based aerial imagery
        "Orthomosaic - Siksik 02.06.2023": {
            "folders": ["doi-tbd", "drone-based aerial imagery"],
            "src": "2023-06-02 - Orthomosaic - Siksik.tif",
            "dst_dir": data_folder / "tvc_data" / "mapping",
            "dst_name": "2023-06-02 - Orthomosaic - Siksik.tif",
            "TBD": True
            },
        "Orthomosaic - Siksik 21.08.2023": {
            "folders": ["doi-tbd", "drone-based aerial imagery"],
            "src": "2023-08-21 - Orthomosaic - Siksik.tif",
            "dst_dir": data_folder / "tvc_data" / "mapping",
            "dst_name": "2023-08-21 - Orthomosaic - Siksik.tif",
            "TBD": True
            },
    # LiDAR-derived DTMs
        "LIDAR DTM - 2024": {
            "folders": ["doi-tbd", "lidar-derived dtms"],
            "src": "2024 - LIDAR - DTM - Siksik.tif",
            "dst_dir": data_folder / "tvc_data" / "mapping",
            "dst_name": "2024 - LIDAR - DTM - Siksik.tif",
            "TBD": True
            },
        "LIDAR DTM HS - 2024": {
            "folders": ["doi-tbd", "lidar-derived dtms"],
            "src": "2024 - LIDAR - HS DTM - Siksik.tif",
            "dst_dir": data_folder / "tvc_data" / "mapping",
            "dst_name": "2024 - LIDAR - HS DTM - Siksik.tif",
            "TBD": True
            },
    # Active Layer Data
        "IWP RTK": {
            "folders": ["doi-tbd", "active layer data"],
            "src": "2025-08-30 - Ice-Wedge-Polygon Summer 2025.kml",
            "dst_dir": data_folder/ "field_data_2025" / "2025-06-30 - Active Layer Depth - RTK",
            "dst_name": "2025-08-30 - Ice-Wedge-Polygon Summer 2025.kml",
            "TBD": True
            },
        "Lysometer RTK": {
            "folders": ["doi-tbd", "active layer data"],
            "src": "2025-08-30 - Lysometer Patch.kml",
            "dst_dir": data_folder/ "field_data_2025" / "2025-06-30 - Active Layer Depth - RTK",
            "dst_name": "2025-08-30 - Lysometer Patch.kml",
            "TBD": True
            },
        "Siksik Lower RTK": {
            "folders": ["doi-tbd", "active layer data"],
            "src": "2025-08-30 - Siksik Lower Summer.kml",
            "dst_dir": data_folder/ "field_data_2025" / "2025-06-30 - Active Layer Depth - RTK",
            "dst_name": "2025-08-30 - Siksik Lower Summer.kml",
            "TBD": True
            },
        "Siksik Middle RTK": {
            "folders": ["doi-tbd", "active layer data"],
            "src": "2025-08-30 - Siksik Middle Summer.kml",
            "dst_dir": data_folder/ "field_data_2025" / "2025-06-30 - Active Layer Depth - RTK",
            "dst_name": "2025-08-30 - Siksik Middle Summer.kml",
            "TBD": True
            },
        "Siksik Upper RTK": {
            "folders": ["doi-tbd", "active layer data"],
            "src": "2025-09-24 - Siksik Upper Summer.kml",
            "dst_dir": data_folder/ "field_data_2025" / "2025-06-30 - Active Layer Depth - RTK",
            "dst_name": "2025-09-24 - Siksik Upper Summer.kml",
            "TBD": True
            },
        "Active Layer Measurements": {
            "folders": ["doi-tbd", "active layer data"],
            "src": "2025-06-30 - Active Layer Depth.xlsx",
            "dst_dir": data_folder/ "field_data_2025",
            "dst_name": "2025-06-30 - Active Layer Depth.xlsx",
            "TBD": True
            },
    # GPR survey data
        "IWP Control Points": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "2025-09-24 - IWP Start and End of Transects.kml",
            "dst_dir": data_folder/ "field_data_2025" / "2025-09-24 - Controll Points",
            "dst_name": "2025-09-24 - IWP Start and End of Transects.kml",
            "TBD": True
            },
        "Siksik Control Points": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "2025-09-24 - Siksik Start and End of Transects.kml",
            "dst_dir": data_folder/ "field_data_2025" / "2025-09-24 - Controll Points",
            "dst_name": "2025-09-24 - Siksik Start and End of Transects.kml",
            "TBD": True
            },
        "Radargram IWP 1-2": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-1-2_S-E.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-1-2_S-E.SGY",
            "TBD": True
            },
        "Radargram IWP 2-3": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-2-3_E-S.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-2-3_E-S.SGY",
            "TBD": True
            },
        "Radargram IWP 3-4": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-3-4_S-E.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-3-4_S-E.SGY",
            "TBD": True
            },
        "Radargram IWP 4-5": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-4-5_S-E.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-4-5_S-E.SGY",
            "TBD": True
            },
        "Radargram IWP 5-6": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-5-6_S-E.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-5-6_S-E.SGY",
            "TBD": True
            },
        "Radargram IWP 6-7": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-6-7_S-E.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-6-7_S-E.SGY",
            "TBD": True
            },
        "Radargram IWP 7-8": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-7-8_S-E.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-7-8_S-E.SGY",
            "TBD": True
            },
        "Radargram IWP 8-9": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-8-9_S-E.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-8-9_S-E.SGY",
            "TBD": True
            },
        "Radargram IWP 9-1": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-9-1_E-S.SGY",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Radargrams",
            "dst_name": "S_500MHZ_IWP-9-1_E-S.SGY",
            "TBD": True
            },
        "Refl Picks IWP 1-2": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-1-2_S-E.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-1-2_S-E.PCK",
            "TBD": True
            },
        "Refl Picks IWP 2-3": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-2-3_E-S.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-2-3_E-S.PCK",
            "TBD": True
            },
        "Refl Picks IWP 3-4": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-3-4_S-E.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-3-4_S-E.PCK",
            "TBD": True
            },
        "Refl Picks IWP 4-5": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-4-5_S-E.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-4-5_S-E.PCK",
            "TBD": True
            },
        "Refl Picks IWP 5-6": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-5-6_S-E.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-5-6_S-E.PCK",
            "TBD": True
            },
        "Refl Picks IWP 6-7": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-6-7_S-E.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-6-7_S-E.PCK",
            "TBD": True
            },
        "Refl Picks IWP 7-8": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-7-8_S-E.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-7-8_S-E.PCK",
            "TBD": True
            },
        "Refl Picks IWP 8-9": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-8-9_S-E.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-8-9_S-E.PCK",
            "TBD": True
            },
        "Refl Picks IWP 9-1": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHZ_IWP-9-1_E-S.PCK",
            "dst_dir": manual_input_folder / "gpr_analysis" / "Reflection Pick Lines",
            "dst_name": "S_500MHZ_IWP-9-1_E-S.PCK",
            "TBD": True
            },
        "GP2 IWP 1-2": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-1-2_S-E.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-1-2_S-E.gp2",
            "TBD": True
            },
        "GP2 IWP 2-3": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-2-3_E-S.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-2-3_E-S.gp2",
            "TBD": True
            },
        "GP2 IWP 3-4": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-3-4_S-E.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-3-4_S-E.gp2",
            "TBD": True
            },
        "GP2 IWP 4-5": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-4-5_S-E.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-4-5_S-E.gp2",
            "TBD": True
            },
        "GP2 IWP 5-6": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-5-6_S-E.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-5-6_S-E.gp2",
            "TBD": True
            },
        "GP2 IWP 6-7": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-6-7_S-E.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-6-7_S-E.gp2",
            "TBD": True
            },
        "GP2 IWP 7-8": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-7-8_S-E.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-7-8_S-E.gp2",
            "TBD": True
            },
        "GP2 IWP 8-9": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-8-9_S-E.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-8-9_S-E.gp2",
            "TBD": True
            },
        "GP2 IWP 9-1": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-9-1_E-S.gp2",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-9-1_E-S.gp2",
            "TBD": True
            },
        "HD IWP 1-2": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-1-2_S-E.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-1-2_S-E.hd",
            "TBD": True
            },
        "HD IWP 2-3": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-2-3_E-S.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-2-3_E-S.hd",
            "TBD": True
            },
        "HD IWP 3-4": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-3-4_S-E.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-3-4_S-E.hd",
            "TBD": True
            },
        "HD IWP 4-5": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-4-5_S-E.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-4-5_S-E.hd",
            "TBD": True
            },
        "HD IWP 5-6": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-5-6_S-E.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-5-6_S-E.hd",
            "TBD": True
            },
        "HD IWP 6-7": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-6-7_S-E.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-6-7_S-E.hd",
            "TBD": True
            },
        "HD IWP 7-8": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-7-8_S-E.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-7-8_S-E.hd",
            "TBD": True
            },
        "HD IWP 8-9": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-8-9_S-E.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-8-9_S-E.hd",
            "TBD": True
            },
        "HD IWP 9-1": {
            "folders": ["doi-tbd", "gpr survey"],
            "src": "S_500MHz_IWP-9-1_E-S.hd",
            "dst_dir": manual_input_folder / "gpr_analysis" / "GNSS_Info",
            "dst_name": "S_500MHz_IWP-9-1_E-S.hd",
            "TBD": True
            },
    # Utility Function data
        "Dempster Highway Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Dempster and Inuvik-Tuktoyaktuk Highway.txt",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Dempster and Inuvik-Tuktoyaktuk Highway.txt",
            "TBD": True
            },
        "Elevation Contours": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Elevation Contours - 2 meter.txt",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Elevation Contours - 2 meter.txt",
            "TBD": True
            },
        "Inuvik Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Inuvik.gpkg",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Inuvik.gpkg",
            "TBD": True
            },
        "Met Station Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Meteorological Station.gpkg",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Meteorological Station.gpkg",
            "TBD": True
            },
        "Rivers Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Natural Earth - Rivers - 10m.txt",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Natural Earth - Rivers - 10m.txt",
            "TBD": True
            },
        "States and Provinces Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Natural Earth - States and Provinces - 10m.txt",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Natural Earth - States and Provinces - 10m.txt",
            "TBD": True
            },
        "Research Site Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Research Site.gpkg",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Research Site.gpkg",
            "TBD": True
            },
        "Trail Valley Creek Station Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Trail Valley Creek Research Station.gpkg",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Trail Valley Creek Research Station.gpkg",
            "TBD": True
            },
        "Tuktoyaktuk Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Tuktoyaktuk.gpkg",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Tuktoyaktuk.gpkg",
            "TBD": True
            },
        "IWP-Transects Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "IWP-Transects.txt",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "IWP-Transects.txt",
            "TBD": True
            },
        "Transect-Points Location": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "Transect-Points.txt",
            "dst_dir": coding_folder / "map_generation" / "Layer Data",
            "dst_name": "Transect-Points.txt",
            "TBD": True
            },
        "Active Layer Thickness Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "active_layer_thickness.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "active_layer_thickness.py",
            "TBD": True
            },
        "Climate Normals Sub Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "climate_normals_utility.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "climate_normals.py",
            "TBD": True
            },
        "Combine Tifs Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "combine_tifs.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "combine_tifs.py",
            "TBD": True
            },
        "General Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "general.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "general.py",
            "TBD": True
            },
        "GNSS Handling Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "gnss_handling.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "gnss_handling.py",
            "TBD": True
            },
        "GPR Plotting  Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "gpr_plotting.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "gpr_plotting.py",
            "TBD": True
            },
        "GPR Processing Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "gpr_processing.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "gpr_processing.py",
            "TBD": True
            },
        "Python to Latex Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "python_to_latex.py",
            "dst_dir": coding_folder / "utility_functions",
            "dst_name": "python_to_latex.py",
            "TBD": True
            },
        "Climate Normals Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "climate_normals.py",
            "dst_dir": coding_folder,
            "dst_name": "climate_normals.py",
            "TBD": True
            },
        "Environment Python": {
            "folders": ["doi-tbd", "utility functions"],
            "src": "environment.py",
            "dst_dir": coding_folder / "config",
            "dst_name": "environment.py",
            "TBD": True
            }
        }

    # Copy targets to correct folders
    for label, info in targets.items():
        print(f"Searching for {label} ...")

        # Check whether file should exist
        truer = False
        if truer == True:
            print(f"  ⏭️  Skipping {label} (File marked 'TBD'.)")
        else:
            # Pre-calculate destination
            dest_path = data_folder / "tvc_data" / info["dst_dir"]
            file_found = False
            # Iterate through potential source folders
            for folder_name in info["folders"]:
                source_file = coding_folder / folder_name / info["src"]
                if source_file.exists():
                    # Create folder and copy
                    dest_path.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_path / info["dst_name"])

                    print(f"  ✅ Found in '{folder_name}'. Copied to {info['dst_name']}")
                    file_found = True
                    # Go next as quickly as possible
                    break
            if file_found == False:
                print(f"  ❌ Could not find source file for {label}")

    print("prepare_analysis_hum_prj.py finished.")
    print("# ====================================================================================================================================================== #")
