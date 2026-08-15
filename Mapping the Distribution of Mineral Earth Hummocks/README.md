# Mapping the Distribution of Mineral Earth Hummocks — Code for MSc Thesis 2nd research chapter

## Abstract

Mineral earth hummocks are one of the most common microtopographic features influencing the northern landscape. These features dictate active layer thickness and hydrological flow paths, playing a critical role in the storage and transport of contaminants such as radionuclides, mercury, and carbon. However, as "shrubification" accelerates across the tundra, traditional optical remote sensing often fails to capture these small-scale features. There is a critical need for robust, high-resolution topographic datasets that can see through dense vegetation to provide accurate inputs for hydrological and permafrost modeling in a warming climate.

This dataset was used for mineral earth hummock mapping in the Master of Science (MSc) thesis of Tobias Leander Leonhard and it evaluates and provides a framework for landscape-scale mapping of mineral earth hummocks in the western Canadian Arctic using 0.5 m resolution LiDAR-derived Digital Terrain Models (DTMs). By implementing a Topographic Position Index (TPI) mapping algorithm and conducting rigorous analytical error propagation, this study distinguishes legitimate geomorphic signals from processing artifacts. Validated against ground-based surveys and Ground Penetrating Radar (GPR), the data captures hummock densities and spatial distributions that are otherwise hidden from optical sensors. This collection is particularly valuable for understanding sub-shrub topography, as it identifies features in areas where over 50% of the hummocks are obscured by shrub cover.

## Project summary

This repository contains all code needed for reproducing the second research chapter of the MSc thesis of Tobias Leander Leonhard who worked in the Arctic Hydrology Research Group at Wilfrid Laurier University and was supervised by Prof. Dr. Philip Marsh and Dr. Elizabeth Priebe.

## Code structure

The repository has the following structure:

```text
├── config/
│   ├── __init__.py                                             # Package marker for Python imports.
│   ├── env.yml                                                 # Conda environment file listing Python dependencies.
│   └── environment_hum_prj.py                                  # Project-specific configuration and environment setup script.
├── manual_input_data/
│   ├── vegetation_mapping/
│   │   └── 2023/
│   │       ├── Lichen.gpkg                                     # Vegetation-classification layer: Lichen.
│   │       ├── Moss.gpkg                                       # Vegetation-classification layer: Moss.
│   │       ├── Shrub.gpkg                                      # Vegetation-classification layer: Shrub.
│   │       └── Tussock.gpkg                                    # Vegetation-classification layer: Tussock.
│   └── excluded_areas_from_hummock_mapping.gpkg                # Geospatial mask defining excluded areas.
├── map_generation/
│   ├── Layer Data/
│   │   ├── Siksik Lower.gpkg                                   # Base map layer: Lower Siksik subarea.
│   │   ├── Siksik Middle.gpkg                                  # Base map layer: Middle Siksik subarea.
│   │   ├── Siksik Upper.gpkg                                   # Base map layer: Upper Siksik subarea.
│   │   └── Stream Channels - Hand Drawn.gpkg                   # Base map layer: Digitized stream channels.
│   └── Maps.qgz                                                # QGIS project file for reproducing maps.
├── utility_functions/
│   ├── __init__.py                                             # Package marker for Python imports.
│   ├── dtm_calculations.py                                     # Functions for DTM metrics.
│   ├── error_propagation_calculations.py                       # Uncertainty logic for the mapping workflow.
│   ├── geo_vector_file_operations.py                           # Helper functions for GIS vector handling.
│   ├── gpr_handling_hum_prj.py                                 # Logic for reading and managing GPR data.
│   ├── gpr_plotting_hum_prj.py                                 # Visualisation routines for GPR profiles.
│   ├── gpr_processing_hum_prj.py                               # Processing routines for GPR.
│   ├── hummock_mapping.py                                      # Core algorithmic routines for hummock detection.
│   └── vegetation_mapping.py                                   # Tools for vegetation-class mapping handling.
├── __init__.py                                                 # Root package marker.
├── compare_hummock_mapping_with_vegetation_classification.py   # Analysis: Links hummock maps to vegetation.
├── error_propagation_calculations.py                           # Analysis: Top-level script for error/uncertainty.
├── gpr_analysis.py                                             # Analysis: Main script for GPR validation and interpretation.
├── hummock_mapping.py                                          # Analysis: Main workflow for hummock mapping.
├── main_functions.py                                           # Shared functions used across multiple analysis scripts.
├── prepare_analysis_hum_prj.py                                 # Setup: Script to prepare input data for analysis.
├── README.md                                                   # Project documentation (abstract, setup, and structure).
├── run_python_analysis.py                                      # Entry Point: Runs the full analysis pipeline.
└── vegetation_mapping.py                                       # Analysis: Top-level script for vegetation classification.
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
Mapping the Distribution of Mineral Earth Hummocks
├── active layer data/                                          # Downloaded and unzipped folder
├── config/
│   ├── __init__.py
│   ├── env.yml
│   └── environment_hum_prj.py
├── drone-based aerial imagery/                                 # Downloaded and unzipped folder
├── gpr survey/                                                 # Downloaded and unzipped folder
├── lidar-derived dtms/                                         # Downloaded and unzipped folder
├── manual_input_data/
│   ├── vegetation_mapping/
│   │   └── 2023/
│   │       ├── Lichen.gpkg
│   │       ├── Moss.gpkg
│   │       ├── Shrub.gpkg
│   │       └── Tussock.gpkg
│   └── excluded_areas_from_hummock_mapping.gpkg
├── map_generation/
│   ├── Layer Data/
│   │   ├── Siksik Lower.gpkg
│   │   ├── Siksik Middle.gpkg
│   │   ├── Siksik Upper.gpkg
│   │   └── Stream Channels - Hand Drawn.gpkg
│   └── Maps.qgz
├── meteorological data/                                        # Downloaded and unzipped folder
├── utility functions/                                          # Downloaded and unzipped folder
├── utility_functions/
│   ├── __init__.py
│   ├── dtm_calculations.py
│   ├── error_propagation_calculations.py
│   ├── geo_vector_file_operations.py
│   ├── gpr_handling_hum_prj.py
│   ├── gpr_plotting_hum_prj.py
│   ├── gpr_processing_hum_prj.py
│   ├── hummock_mapping.py
│   └── vegetation_mapping.py
├── __init__.py
├── compare_hummock_mapping_with_vegetation_classification.py
├── error_propagation_calculations.py
├── gpr_analysis.py
├── hummock_mapping.py
├── prepare_analysis_hum_prj.py
├── main_functions.py
├── README.md
├── run_python_analysis.py
└── vegetation_mapping.py
```

Next install the needed python environment using `env.yml`.
Then run `run_python_analysis.py` for running the whole analysis script.
The maps shown in the thesis can be reproduced by using the `Maps.qgz` project.
