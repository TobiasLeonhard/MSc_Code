#     #     #      # #######   #######
#    # #    #      # #     #  #
#   #   #   #      # #     # #
#  #     #  ######## ####### #   #####
# ######### #      # #   #   #       #
# #       # #      # #    #   #     #
# #       # #      # #     #   #####
# Arctic Hydrology Research Group - Wilfrid Laurier University
"""
vegetation_mapping.py

This file contains the vegetation classifier class.

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
from config.environment import *
from utility_functions.python_to_latex import export_to_latex
# ============================================================ #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
class VegetationClassifier:
    """
    Class for running vegetation classifications
    """
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
    def __init__(self, image_path: Path, polygons_path: Path, target_epsg_crs: int, output_folder: Path, test_size: float, model_type: str, dpi: int):
        """
            Init function, initiating the class.
            image_path - Path: Path to the file to classify
            polygons_path - Path: Path to the file in which the polygons are stored
            target_epsg_crs - Int: Integer code of the wanted CRS in EPSG format
            output_folder - Path: Folder used to store output files
            test_size - Float: Fraction of how much of the polygons are used for testing
            model_type - String: Defining the model used (currently only Random Forest is implemented)
            dpi - Int: DPI used for plotting
        """
        self.image_path = Path(image_path)
        self.polygons_path = Path(polygons_path)
        self.target_epsg_crs = target_epsg_crs
        self.output_folder = Path(output_folder)
        self.model_type = model_type
        self.test_size = test_size
        self.dpi = dpi
        self.class_id_col = "class_id"
        self.class_name_col = "class_name"
        self.class_map = {}
        if model_type in ["random_forest", "rf", "RF", "RandomForest"]:
            self.model = RandomForestClassifier(
                n_estimators = 100,
                n_jobs = -1,
                random_state = 42
                )
            self.model_name = "Random Forests"
        else:
            raise ValueError(f"{model_type} unkown and needs implementation.")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
    def _load_polygons(self) -> gpd.GeoDataFrame:
        """
        Function to load polygons.
        If the used path is a folder, all ".gpkg" files are assumed to be polygon classifiers.
        If the path is a file, the file is assumed to contain all classifiers.
        Cleans overlaping polygons
        Returns:
            gdf - Geopandas.DataFrame: A gdf file that contains the polygons.
        """
        if self.polygons_path.is_dir():
            print("Merging multiple geopackages...")
            # Initiate gdf_list
            gdf_list = []

            # Load vec_files and check whether there are any
            vec_files = sorted(list(self.polygons_path.glob("*.gpkg")))
            if not vec_files:
                raise ValueError("No .gpkg files found in polygons_path")

            # Loop through sorted list of files and load the polygons into a gdf
            for i, path in enumerate(vec_files, 1):
                temp_gdf = gpd.read_file(path).to_crs(self.target_epsg_crs)

                # Assign labels
                temp_gdf[self.class_name_col] = path.stem
                temp_gdf[self.class_id_col] = i

                self.class_map[i] = path.stem
                # Add gdf to list
                gdf_list.append(temp_gdf)

            # Merge gdf_list into one gdf
            gdf = gpd.GeoDataFrame(
                pd.concat(
                    gdf_list,
                    ignore_index=True
                    ),
                crs = self.target_epsg_crs
                )

        else:
            print(f"Loading single file: {self.polygons_path}")
            gdf = gpd.read_file(self.polygons_path).to_crs(self.target_epsg_crs)

            if self.class_id_col not in gdf.columns:
                raise ValueError(f"Column '{self.class_id_col}' missing in {self.polygons_path}")


        print("Checking for overlapping polygons...")
        # Spatial join to find intersections
        joined = gpd.sjoin(
            gdf,
            gdf,
            how = "inner",
            predicate = "intersects"
            )

        # Filter out self-intersections
        overlaps_df = joined[joined.index != joined["index_right"]].copy()

        if not overlaps_df.empty:
            # Helper to check if they only touch at the edge
            def check_is_actual_overlap(row, df):
                geom1 = df.geometry.loc[row.name]
                geom2 = df.geometry.loc[row["index_right"]]
                # If they only touch at boundaries, it's not a classification conflict
                return not geom1.touches(geom2)

            # Apply the check using the local gdf
            overlaps_df["is_conflict"] = overlaps_df.apply(lambda r: check_is_actual_overlap(r, gdf), axis=1)
            actual_conflicts = overlaps_df[overlaps_df["is_conflict"] == True]

            if not actual_conflicts.empty:
                conflict_indices = actual_conflicts.index.unique()
                final_overlap_gdf = gdf.loc[conflict_indices]

                over_lap_file = self.output_folder / "overlapping_polygons.gpkg"
                print(f"Found {len(final_overlap_gdf)} overlapping polygons. Saving to {over_lap_file}")
                final_overlap_gdf.to_file(over_lap_file, driver = "GPKG")

                # Drop the conflicting polygons from training
                gdf = gdf.drop(index = conflict_indices)
                print(f"Removed {len(conflict_indices)} conflicting polygons from training set.")

        return gdf

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
    def _extract_data(self, src: rasterio.io.DatasetReader, gdf: gpd.GeoDataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extracts data from a given data source and given polygons.

        Args:
            src - DatasetReader: Data source
            gdf - GeoDataFrame: Polygons
        Returns:
            features - ndarray: Stacked pixel values of extracted polygons.
            labels - ndarry: Class ID for each pixel.
        """
        # Checks:
        # 1. Check whether gdf is empty
        gdf = gdf.dropna(subset = ["geometry"])
        gdf = gdf[~gdf.geometry.is_empty]
        if len(gdf) == 0:
            raise ValueError("There data frame is empty.")
        # 2. Check the nodata values of src
        if src.nodata is not None:
            nodata_val = src.nodata
        else:
            nodata_val = 0

        # Initiate lists
        features_list = []
        labels_list = []

        for _, row in gdf.iterrows():
            try:
                # Use the mask function with the explicit nodata value
                out_image, _ = mask(
                    src,
                    [row.geometry],
                    crop = True,
                    nodata = nodata_val
                    )

                # out_image shape is (bands, rows, cols) we reshape to (pixels, bands)
                pixels = out_image.reshape(src.count, -1).T

                # Filter out pixels that are NoData across ALL bands
                valid_mask = np.any(pixels != nodata_val, axis = 1)
                valid_pixels = pixels[valid_mask]

                if valid_pixels.size > 0:
                    features_list.append(valid_pixels)
                    labels_list.append(np.full(len(valid_pixels), row[self.class_id_col]))

            except ValueError as e:
                # Polygon is outside of the raster?
                print(f"Skipping polygon {row.name}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error on polygon {row.name}: {e}")
                continue

        if not features_list:
            raise ValueError("No valid pixels found for training. Check if your polygons overlap the image.")

        features = np.vstack(features_list)
        labels = np.concatenate(labels_list)
        return features, labels

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
    def wite_report(self, pred_report: Union[dict, str], test: np.ndarray, pred: np.ndarray):
        """
        Generates a report in the form of a table and a heat map using prediction report values, test values, and prediciton values.

        Args:
            pred_repirt - dict: Report Dictonary
            test - ndarry: Test values
            pred - ndarry: Prediciton values
        """
        if isinstance(pred_report, str):
            raise ValueError("String type report handling is not implemented here.")
        # Load the class mapping and save it as a CSV for reference
        class_map = pd.DataFrame.from_dict(self.class_map, orient='index', columns=['Class Name'])
        class_map.to_csv(self.output_folder / f"class_legend_{self.model_type}.csv")

        pred_accuracy = pred_report["accuracy"]
        report_df = pd.DataFrame(pred_report).T

        # Create confusion matrix DataFrame
        labels = sorted(list(set(test))) # Get class names (1, 2, 3, 4)
        cm = confusion_matrix(test, pred, labels=labels)
        cm_df = pd.DataFrame(cm, index=labels, columns=labels)

        report_df["Reported Value"] = None
        report_df = report_df.drop("accuracy")
        # Rename the index to class names using the class_map
        for i, row in class_map.iterrows():
            report_df.loc[str(i), "Reported Value"] = row["Class Name"]
            cm_df.rename(index={str(i): row["Class Name"]}, inplace=True)
            cm_df.rename(columns={str(i): row["Class Name"]}, inplace=True)
            labels = [row["Class Name"] if str(label) == str(i) else label for label in labels]

        if "macro avg" in report_df.index:
            report_df.at["macro avg", "Reported Value"] = "Macro Avg."
        if "weighted avg" in report_df.index:
            report_df.at["weighted avg", "Reported Value"] = "Weighted Avg."
        report_df = report_df[
            [
                "Reported Value",
                "precision",
                "recall",
                "f1-score",
                "support"
                ]
            ]
        report_df.rename(columns = {
           "precision": "Precision",
           "recall": "Recall",
           "f1-score": "F1-Score",
           "support": "Support",
           },
           inplace = True
           )
        caption = (
            f"{self.model_name} Classification Results",
            f"{self.model_name} Macro-report of classification results from the performed vegetation classificaiton.\nThe reported accuracy is {pred_accuracy:.3f}.\n"
            )
        precision_dict = {
            r"Reported Value": None,
            r"Precision": 2,
            r"Recall": 2,
            r"F1-Score": 2,
            r"Support": 0,
            }
        export_to_latex(
            data = report_df,
            caption = caption,
            precision_dict = precision_dict,
            label = f"tab:classification_results_{self.model_type}",
            float_placement_identifier = "",
            output_path = self.output_folder / f"table_{self.model_type}.tex",
            column_based = True
            )

        # Save confusion matrix as CSV
        cm_df.to_csv(self.output_folder / f"confusion_matrix_{self.model_type}.csv")

        # Generate and save Visual Heatmap (PNG)
        cmap = LinearSegmentedColormap.from_list("custom_purple", ["#ffffff", custom_colors["wlu_purple"]])
        fig, ax = plt.subplots(figsize=(10, 10))
        disp = ConfusionMatrixDisplay.from_predictions(
            test,
            pred,
            display_labels = labels,
            cmap = cmap,
            normalize = "true",
            ax = ax
            )
        ax.set_title(f"Confusion Matrix of {self.model_name} Classification\n(Normalized)")

        # Save the image
        plt.savefig(self.output_folder / f"confusion_matrix_visual_{self.model_type}.png", dpi = self.dpi)
        plt.close()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
    def run_pipeline(self):
        """
        Pipeline to run a full classification
        """
        self.output_folder.mkdir(parents=True, exist_ok=True)

        with rasterio.open(self.image_path) as src:
            # 1. Load nodata value from source or default to 0
            if src.nodata is not None:
                src_nodata = src.nodata
            else:
                src_nodata = 0

            gdf = self._load_polygons()

            # Split data into training and testing sets
            train_gdf, test_gdf = train_test_split(
                gdf,
                test_size = self.test_size,
                stratify = gdf[self.class_id_col],
                random_state = 42
                )

            print("Extracting training features...")
            X_train, y_train = self._extract_data(src, train_gdf)
            X_test, y_test = self._extract_data(src, test_gdf)

            print(f"Training model on {len(y_train)} pixels...")
            self.model.fit(X_train, y_train - 1) # Subtract 1 to convert class IDs to 0-based for sklearn

            # Create report
            y_pred = self.model.predict(X_test) + 1 # Add 1 to convert back to original class IDs
            report = classification_report(y_test, y_pred, output_dict=True)

            # Write the report to LaTeX
            self.wite_report(
                pred_report = report,
                test = y_test,
                pred = y_pred
                )

            # Windowed Prediction
            print("Predicting image in blocks...")
            meta = src.meta.copy()
            # Ensure output is uint8 and nodata is explicitly set to 0
            meta.update(count = 1, dtype = "uint8", nodata = 0)

            with rasterio.open(self.output_folder / f"vegetation_classification_map_{self.model_type}.tif", 'w', **meta) as dst:
                for _, window in src.block_windows(1):
                    # Read all bands for the current window
                    block_data = src.read(window = window)
                    bands, h, w = block_data.shape

                    # Create a mask: True where there is actual data
                    # A pixel is valid if ANY band is not equal to nodata
                    valid_mask = np.any(block_data != src_nodata, axis = 0)

                    # Initialize an empty block with the output nodata value (0)
                    prediction_block = np.zeros((h, w), dtype=np.uint8)

                    # Only run prediction if there are valid pixels in this window
                    if np.any(valid_mask):
                        # Flatten the block for the model (pixels, bands)
                        flat_pixels = block_data.reshape(bands, -1).T
                        # Create a flat mask for valid pixels
                        flat_mask = valid_mask.ravel()

                        # Extract only valid pixels for prediction
                        valid_pixels = flat_pixels[flat_mask]

                        # Check if there are valid pixels to predict
                        if valid_pixels.size > 0:
                            # Predict and convert back to original class IDs
                            raw_predictions = self.model.predict(valid_pixels)
                            # Convert predictions back to original class IDs (add 1) and ensure they fit in uint8
                            final_predictions = (raw_predictions + 1).astype(np.uint8)

                            # Place predictions back into the block
                            prediction_block.ravel()[flat_mask] = final_predictions

                    dst.write(prediction_block, 1, window=window)

            print(f"Success! Map saved in {self.output_folder}")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ #
