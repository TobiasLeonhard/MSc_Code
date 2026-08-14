# Mapping the Distribution of Mineral Earth Hummocks — Code for MSc Thesis 2nd research chapter

## Abstract

Mineral earth hummocks are one of the most common microtopographic features influencing the northern landscape. These features dictate active layer thickness and hydrological flow paths, playing a critical role in the storage and transport of contaminants such as radionuclides, mercury, and carbon. However, as "shrubification" accelerates across the tundra, traditional optical remote sensing often fails to capture these small-scale features. There is a critical need for robust, high-resolution topographic datasets that can see through dense vegetation to provide accurate inputs for hydrological and permafrost modeling in a warming climate.

This dataset was used for mineral earth hummock mapping in the Master of Science (MSc) thesis of Tobias Leander Leonhard and it evaluates and provides a framework for landscape-scale mapping of mineral earth hummocks in the western Canadian Arctic using 0.5 m resolution LiDAR-derived Digital Terrain Models (DTMs). By implementing a Topographic Position Index (TPI) mapping algorithm and conducting rigorous analytical error propagation, this study distinguishes legitimate geomorphic signals from processing artifacts. Validated against ground-based surveys and Ground Penetrating Radar (GPR), the data captures hummock densities and spatial distributions that are otherwise hidden from optical sensors. This collection is particularly valuable for understanding sub-shrub topography, as it identifies features in areas where over 50% of the hummocks are obscured by shrub cover.

The Arctic mineral earth hummock dataset described here includes:
High-Resolution Digital Terrain Models (DTMs): 0.5 m resolution LiDAR-derived elevation products.
Geophysical Validation Data: Ground Penetrating Radar (GPR) profiles and ground-based validation points used to verify hummock presence and geometry and ground validation data derived from frost probing.
Drone-based orthomosaic data used for a vegetation classification.

## Project summary

This repository contains all code needed for reproducing the second research chapter of the MSc thesis of Tobias Leander Leonhard who worked in the Arctic Hydrology Research Group at Wilfrid Laurier University and was supervised by Prof. Dr. Philip Marsh and Dr. Elizabeth Priebe.

## Code structure

The project has the following structure:

```text
├── config/
│   ├── environment.py      # Import hub that is used to import all needed libraries for the subproject
│   ├── env.yml             # YML file for creating the python environment
├── map_generation/         # QGIS project for map creation (has dependencies in the data and manual_input_folder)
├── utility_functions/      # Reusable functions or custom modules
├── main_functions.py       # Different functions to handle the utility functions
├── README.md               # Read me file for each project
└── run_python_analysis.py  # Python file that runs all main functions files in the order needed to reflect on dependencies
```

## Setup

Download the code and the linked repositories.
[meteorological data](https://doi.org/10.5683/SP3/BXV4DE).
[active layer data](https://borealisdata.ca/dataverse/trailvalley).
[gpr survey](https://borealisdata.ca/dataverse/trailvalley).
[lidar-derived dtms](https://borealisdata.ca/dataverse/trailvalley).
[drone-based aerial imagery](https://borealisdata.ca/dataverse/trailvalley).
[utility functions](https://borealisdata.ca/dataverse/trailvalley).

Unzipp all downloads and move them into one folder, here called "Mapping the Distribution of Mineral Earth Hummocks", so you get the following structure:

```text
Mapping the Distribution of Mineral Earth Hummocks
├── active layer data/                                          # Downloaded and unzipped folder
├── config/
│   ├── environment.py
│   └── env.yml
├── drone-based aerial imagery/                                 # Downloaded and unzipped folder
├── gpr survey/                                                 # Downloaded and unzipped folder
├── lidar-derived dtms/                                         # Downloaded and unzipped folder
├── map_generation/
│   ├── Layer Data/
│   │   ├── Siksik Lower.gpkg
│   │   ├── Siksik Middle.gpkg
│   │   ├── Siksik Upper.gpkg
│   │   ├── Siksik-Transects.gpkg
│   │   └── Stream Channels - Hand Drawn.gpkg
│   └── Maps.qgz
├── meteorological data/                                        # Downloaded and unzipped folder
├── utility_functions/
│   ├── dtm_calculations.py
│   ├── error_propagation_calculations.py
│   ├── geo_vector_file_operations.py
│   ├── gpr_handling_hum_prj.py
│   ├── gpr_plotting_hum_prj.py
│   ├── gpr_processing_hum_prj.py
│   ├── hummock_mapping.py
│   └── vegetation_mapping.py
├── utility functions/                                          # Downloaded and unzipped folder
├── compare_hummock_mapping_with_vegetation_classification.py
├── error_propagation_calculations.py
├── gpr_analysis.py
├── hummock_mapping.py
├── prepare_analysis_hum_prj.py
├── README.md
├── run_python_analysis.py
└── vegetation_mapping.py
```

Next install the needed python environment using `env.yml` and prepare the project by running `run_python_analysis.py`.
This will automatically sort the downloaded and unzipped folders in the correct subfolders for analysis.
Then run `run_python_analysis.py` for running the whole analysis script.
The maps shown in the thesis can be reproduced by using the `Maps.qgz` project.
