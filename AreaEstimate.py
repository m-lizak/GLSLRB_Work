"""
Author: Maciej Lizak

This script calculates wetland area estimates by class from raster classification outputs.
It masks prediction rasters to basin boundary shapefiles, counts pixel classes within the basin,
and converts pixel counts to area in square kilometers. The results are saved to Excel files.
"""

import os
import numpy as np
import rasterio
import pandas as pd
import fiona
from rasterio.mask import mask

# Define the list of basins to process - here only "Superior" as example
basins = ["Superior", "Huron", "Erie", "Ontario", "Lawrence", "GLSLRB"]

# Mapping of raster pixel values to wetland class names
class_mapping = {
    1: "bog",
    2: "fen",
    3: "swamp",
    4: "marsh",
    5: "water"
}

# Pixel area in square kilometers (30 m x 30 m pixel = 900 m² = 0.0009 km²)
PIXEL_AREA_KM2 = 0.0009

# Expected Coordinate Reference System for inputs (NAD83 / Statistics Canada Lambert)
EXPECTED_CRS = "EPSG:3348"

def calculate_wetland_area(input_folder, output_path, basin_name):
    """
    Calculate wetland area by class for raster classification outputs,
    masking each raster to the basin boundary polygon(s).

    Parameters:
        input_folder (str): Directory containing raster prediction files.
        output_path (str): Path to save the resulting Excel summary.
        basin_name (str): Basin identifier used to locate shapefile and label output.
    """
    # Load basin boundary shapefile and extract geometries for masking
    shapefile_path = f"/home/mlizak/modelClassifications/boundaryShapefiles/USCAN/{basin_name}/{basin_name}Boundaries.shp"
    with fiona.open(shapefile_path, "r") as shapefile:
        geometries = [feature["geometry"] for feature in shapefile]
        shapefile_crs = shapefile.crs

    # Warn if shapefile CRS does not match expected CRS
    if shapefile_crs != EXPECTED_CRS:
        print(f"Warning: Shapefile CRS is {shapefile_crs}, expected {EXPECTED_CRS}")

    # Dictionary to store cumulative pixel counts by model and wetland class
    results = {}

    # Identify all raster files (.tif or .img) in input folder
    raster_files = [f for f in os.listdir(input_folder) if f.endswith(('.tif', '.img'))]

    # Loop through each raster file for processing
    for filename in raster_files:
        raster_path = os.path.join(input_folder, filename)

        with rasterio.open(raster_path) as src:
            # Verify CRS of raster; warn if different than expected
            if src.crs != EXPECTED_CRS:
                print(f"Warning: Raster {filename} CRS is {src.crs}, expected {EXPECTED_CRS}")
            # If raster and shapefile CRS differ, skip this raster
            if src.crs != shapefile_crs:
                print(f"Error: CRS mismatch - Raster: {src.crs}, Shapefile: {shapefile_crs}")
                continue

            # Mask raster to basin boundary polygons; crops to extent
            try:
                masked_data, _ = mask(src, geometries, crop=True, nodata=src.nodata)
            except ValueError as e:
                print(f"Skipping {filename}: {e}")
                continue

            # Get descriptive band names or fallback to generic "Band_X"
            band_names = [
                src.descriptions[i] if src.descriptions and src.descriptions[i] else f"Band_{i+1}"
                for i in range(src.count)
            ]

            # Process each band separately (for multi-band rasters)
            for band_idx in range(src.count):
                model_name = band_names[band_idx]

                # Initialize nested dict for this model if not exists
                if model_name not in results:
                    results[model_name] = {cls: 0 for cls in class_mapping}

                band_data = masked_data[band_idx]

                # Filter out nodata pixels before counting classes
                if src.nodata is not None:
                    valid_pixels = band_data[band_data != src.nodata]
                else:
                    valid_pixels = band_data.flatten()

                # Skip if no valid pixels after masking
                if valid_pixels.size == 0:
                    continue

                # Count pixel frequency per class value in valid pixels
                unique, counts = np.unique(valid_pixels, return_counts=True)
                class_counts = dict(zip(unique, counts))

                # Add counts to cumulative results for each class
                for cls in class_mapping:
                    results[model_name][cls] += class_counts.get(cls, 0)

    # Convert results dict into a pandas DataFrame for export
    data = [
        {
            "Model": model,
            "Class": class_mapping[cls],
            "Pixel_Count": count,
            "Area_km2": count * PIXEL_AREA_KM2
        }
        for model in results
        for cls, count in results[model].items()
    ]
    df = pd.DataFrame(data)

    # Save results to Excel file if any data was processed
    if not df.empty:
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"Saved {basin_name} wetland area estimates to {output_path}")
    else:
        print(f"No data processed for {basin_name}")

# Main execution: process all basins listed
for basin in basins:
    input_folder = f"/home/mlizak/modelClassifications/predictionRasters/{basin}"
    output_file = f"/home/mlizak/modelClassifications/areaEstimate/wetlandAreas{basin}.xlsx"
    print(f"Processing basin: {basin}...")
    try:
        calculate_wetland_area(input_folder, output_file, basin)
    except Exception as e:
        print(f"Failed to process {basin}: {e}")
