## Wetland Area Calculation Script

This script calculates wetland area estimates from classified raster prediction outputs by masking them to defined basin boundaries. It automates the process of extracting pixel counts for multiple wetland classes (e.g., bog, fen, swamp, marsh, water), converting these counts into area estimates (in km²), and saving the results in Excel format for further analysis.

### Key Features

- Supports batch processing of multiple basins (currently configured for "Superior").
- Masks raster datasets to shapefile-defined basin boundaries to isolate the study area.
- Checks and verifies coordinate reference system (CRS) consistency between rasters and shapefiles.
- Handles multi-band raster files, interpreting each band as a separate classification model.
- Summarizes pixel counts by wetland class and converts counts to area using pixel size.
- Outputs tabular results with model name, wetland class, pixel count, and area in km².
- Saves results as Excel files for easy reporting and integration with other workflows.

### Configuration

- **Basins:** Set the list of basin names to process in the `basins` variable.
- **Class Mapping:** Edit the `class_mapping` dictionary to reflect the integer class codes and their corresponding wetland type names.
- **Pixel Area:** Adjust the `PIXEL_AREA_KM2` constant if working with different raster resolutions.
- **CRS:** Confirm that rasters and shapefiles use the expected CRS defined in `EXPECTED_CRS` (`EPSG:3348` by default).

### File Structure Assumptions
- Raster prediction files are located in `/home/mlizak/modelClassifications/predictionRasters/{BASIN_NAME}`.
- Basin boundary shapefiles are stored in `/home/mlizak/modelClassifications/boundaryShapefiles/USCAN/{BASIN_NAME}/`.
- Output Excel files will be saved to `/home/mlizak/modelClassifications/areaEstimate/` with filenames `wetlandAreas{BASIN_NAME}.xlsx`.

### Dependencies
- Python libraries: `numpy`, `pandas`, `rasterio`, `fiona`, `openpyxl`.

### Usage
Run the script as-is to process the configured basins and generate wetland area summaries. Modify the `basins` list and paths as needed to suit your data organization.

---

*Script author: Maciej Lizak*

