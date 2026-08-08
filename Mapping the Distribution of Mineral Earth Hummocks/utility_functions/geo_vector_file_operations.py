#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
geo_vector_file_operations.py

Utility functions for handling and creating geo vector files ('.gpkg').

Author: Tobias Leonhard
Project: MSc Thesis
Research Group: Arctic Hydrology Research Group (AHRG), Wilfrid Laurier University
Created: 2025
Last Modified: 2026-08-06
Version: 1.0
"""

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
# ============================================================ #
import sys
from pathlib import Path
parent_folder = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_folder))
from config.environment import *
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
def polygonize_raster_to_vector(raster_path: Path, vector_path: Path, connectivity: int, values_are_boolean: bool, property_key: str) -> Path:
    """
    Converts a raster file to a vector file with a defined connectivity.
    If values_are_boolean is True, only raster pixel with value 1 are polygonized.

    Args:
        raster_path - Path: File path to the input raster file
        vector_path - Path: File path to the output vector file
        connectivity - int: Connectivity type (4 or 8).
        values_are_boolean - bool: Boolean value do distinct differnet polygonizing styles
        property_key - str: Name of the property key
    Returns:
        output_vector_path - Path: File path to the output vector file
    """
    # Check connectivty style
    if connectivity not in [4, 8]:
        raise ValueError("Connectivity must be either 4 or 8.")

    # Check whether vector path has a suffix
    if not vector_path.suffix:
        vector_path = vector_path.with_suffix(".gpkg")
    elif vector_path.suffix == ".tif":
        vector_path = vector_path.with_suffix(".gpkg")

    if not vector_path.exists():
        # Open raster
        with rasterio.open(raster_path) as src:
            # Check for number of bands
            if src.count > 1:
                raise ValueError(f"Function only designed for one band. Found {src.count} bands.")

            # Determine data type for schema
            raw_dtype = src.dtypes[0]
            schema_type = "int" if "int" in raw_dtype else "float"
            schema = {"geometry": "Polygon", "properties": {property_key: schema_type}}

            # Check whether RAM or Disk processing is needed
            pixels = src.width * src.height
            use_ram = pixels < 1_000_000_000 # ~1GB limit for 1-byte pixels

            if use_ram:
                image_data = src.read(1)
                # Create mask only if necessary to save RAM
                mask = (image_data == 1) if values_are_boolean else None
            else:
                # For streaming, we use the Band object
                image_data = rasterio.band(src, 1)
                mask = src.dataset_mask() if not values_are_boolean else None
                if values_are_boolean and not use_ram:
                    image_data = src.read(1)
                    mask = (image_data == 1)

            with fiona.open(vector_path, "w", driver="GPKG", crs=src.crs, schema=schema) as dst:
                # Generate shapes
                shape_gen = rasterio.features.shapes(
                    image_data,
                    mask = mask,
                    connectivity = connectivity,
                    transform = src.transform
                    )

                # Process in batches
                batch_size = 1000
                batch = []
                for geom, value in shape_gen:
                    if values_are_boolean and value != 1:
                        continue

                    batch.append({
                        "geometry": geom,
                        "properties": {property_key: value}
                        })

                    if len(batch) >= batch_size:
                        dst.writerecords(batch)
                        batch = []

                if batch:
                    dst.writerecords(batch)

    return vector_path

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
