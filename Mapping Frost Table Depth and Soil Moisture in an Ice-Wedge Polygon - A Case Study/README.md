# Mapping Frost Table Depth and Soil Moisture in an Ice-Wedge Polygon - A Case Study — Code for MSc Thesis 1st research chapter

## Abstract

Across Arctic lowland permafrost landscapes, ice-wedge polygons (IWPs) serve as critical regulators of local hydrology, topographic evolution, and biogeochemical cycling. While aggrading IWPs traditionally act as sinks for water and pollutants, such as radionuclides, carbon, and mercury, rapid permafrost thaw is transitioning these features into potential sources of contaminants. Characterizing these changes is a significant concern for Arctic stakeholders, yet the extreme spatial heterogeneity of IWPs makes monitoring active layer dynamics challenging using traditional methods alone.

This dataset provides a high-resolution characterization of frost table dynamics and soil moisture variability at an ice-wedge polygon site located near the Laurier Trail Valley Creek Research Station (TVC-RS) in the western Canadian Arctic. By integrating traditional frost probing with advanced geophysical and remote sensing techniques, this research captures the complex subsurface architecture of the tundra. The data highlights a landscape in transition, documenting the presence of high-centered polygons (HCPs) and the ongoing degradation of ice wedges. This collection serves as a baseline for quantifying how deepening frost tables and shifting soil moisture regimes influence local drainage, water storage, and the potential release of stored contaminants.

The high-resolution IWP dataset described here includes: Ground Penetrating Radar (GPR) Profiles: 500 MHz GPR survey data across ten transects. Frost Table Measurements Light Detection and Ranging (LiDAR) and Unmanned Aerial Vehicle (UAV) datasets providing precise surface elevations and vegetation context.

The GPR and ground-probing data was recorded in 2025, the LiDAR data in 2024, and the orthomosaic data in 2023.

## Project summary

This repository contains all code needed for reproducing the first research chapter of the MSc thesis of Tobias Leander Leonhard who worked in the Arctic Hydrology Research Group at Wilfrid Laurier University and was supervised by Prof. Dr. Philip Marsh and Dr. Elizabeth Priebe.

## Code structure

The repository has the following structure:

```text
├── config/
│   ├── __init__.py                                                     # Package marker for Python imports.
│   ├── env.yml                                                         # Conda environment file listing Python dependencies.
│   └── environment_iwp_prj.py                                          # Project-specific configuration and environment setup script.
├── manual_input_data/
│   ├── area_defined_as_subsidence_free_center.gpkg                     # Geospatial mask defining subsidence free center.
│   └── outline_of_ice_wedge_polygon_study_site.gpkg                    # Geospatial mask defining outline of ice-wedge polygon area
├── map_generation/
│   ├── Layer Data/
│   │   ├── Ice-Wedge Polygon (IWP).gpkg                                # Base map layer: Ice-wedge polygon area.
│   │   └── Stream Channels - Hand Drawn - Including IWP.gpkg.gpkg      # Base map layer: Digitized stream channels.
│   └── Maps.qgz                                                        # QGIS project file for reproducing maps.
├── utility_functions/
│   ├── __init__.py                                                     # Package marker for Python imports.
│   ├── gpr_handling_iwp_prj.py                                         # Logic for reading and managing GPR data.
│   ├── gpr_plotting_iwp_prj.py                                         # Visualisation routines for GPR profiles.
│   └── gpr_processing_iwp_prj.py                                       # Processing routines for GPR.
├── __init__.py                                                         # Root package marker.
├── bulk_volumetric_soil_water_content_parameterization_comparison.py   # Visualization: Showing differences in parameterizations
├── gpr_analysis.py                                                     # Analysis: Main script for GPR validation and interpretation.
├── prepare_analysis_iwp_prj.py                                         # Setup: Script to prepare input data for analysis.
├── README.md                                                           # Project documentation (abstract, setup, and structure).
├── run_python_analysis.py                                              # Entry Point: Runs the full analysis pipeline.
└── trough_mapping.py                                                   # Analysis: Top-level script for trough mapping.
```

## Setup

Download the code and the linked repositories.
[meteorological data](https://doi.org/10.5683/SP3/BXV4DE).
[active layer data](https://borealisdata.ca/dataverse/trailvalley).
[gpr survey](https://borealisdata.ca/dataverse/trailvalley).
[lidar-derived dtms](https://borealisdata.ca/dataverse/trailvalley).
[drone-based aerial imagery](https://borealisdata.ca/dataverse/trailvalley).
[utility functions](https://borealisdata.ca/dataverse/trailvalley).

Unzipp all downloads and move them into one folder, here called "Mapping the Distribution of Mineral Earth Hummocks", so you get the following structure, with the downloaded folders either named as downloaded (doi...) or renamed as here:

```text
Mapping Frost Table Depth and Soil Moisture in an Ice-Wedge Polygon - A Case Study
├── active layer data/                                                  # Downloaded and unzipped folder
├── config/
│   ├── __init__.py
│   ├── env.yml
│   └── environment_iwp_prj.py
├── drone-based aerial imagery/                                         # Downloaded and unzipped folder
├── gpr survey/                                                         # Downloaded and unzipped folder
├── lidar-derived dtms/                                                 # Downloaded and unzipped folder
├── manual_input_data/
│   ├── area_defined_as_subsidence_free_center.gpkg
│   └── outline_of_ice_wedge_polygon_study_site.gpkg
├── map_generation/
│   ├── Layer Data/
│   │   ├── Ice-Wedge Polygon (IWP).gpkg
│   │   └── Stream Channels - Hand Drawn - Including IWP.gpkg.gpkg
│   └── Maps.qgz
├── meteorological data/                                                # Downloaded and unzipped folder
├── utility functions/                                                  # Downloaded and unzipped folder
├── utility_functions/
│   ├── __init__.py
│   ├── gpr_handling_iwp_prj.py
│   ├── gpr_plotting_iwp_prj.py
│   └── gpr_processing_iwp_prj.py
├── __init__.py
├── bulk_volumetric_soil_water_content_parameterization_comparison.py
├── gpr_analysis.py
├── prepare_analysis_iwp_prj.py
├── README.md
├── run_python_analysis.py
└── trough_mapping.py
```

Next install the needed python environment using `env.yml`.
Then run `run_python_analysis.py` for running the whole analysis script.
The maps shown in the thesis can be reproduced by using the `Maps.qgz` project.
