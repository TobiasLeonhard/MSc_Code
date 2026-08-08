# Mapping the Distribution of Mineral Earth Hummocks — Code for MSc Thesis 2nd research chapter

## Project summary

This repository contains all code needed for reproducing the second research chapter of the MSc thesis of Tobias Leander Leonhard who worked in the Arctic Hydrology Research Group at Wilfrid Laurier University and was supervised by Prof. Dr. Philip Marsh and Dr. Elizabeth Priebe.

In addition to the code, the data is available on the Borealis webpage of the [Trail Valley Creek Research Station](https://borealisdata.ca/dataverse/trailvalley). The data on Borealis is expected to be published before August 24, 2026.

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

## Mapping the Distribution of Mineral Earth Hummocks

This folder contains all code needed to reproduce the second research chapter of the MSc thesis of Tobias Leander Leonhard.
It uses LiDAR data for detecting mineral earth hummocks and uses ground data for validation.
Drone-based orthomosaic data was used for a vegetation classification using random forests.

## Setup

The code itself can only run after the data was downloaded from Borealis. There is also another dependency with [meteorological data](https://doi.org/10.5683/SP3/BXV4DE). For the project the folders "data" and "manual_input_data" are needed.
