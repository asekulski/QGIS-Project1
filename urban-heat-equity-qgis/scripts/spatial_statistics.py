"""
QGIS Processing Script: Spatial Statistics & AI-Ready Feature Engineering

Generates spatial statistics and prepares features for machine learning models.
Demonstrates advanced geospatial analysis techniques relevant to AI research.
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsField, QgsFeature,
    QgsGeometry, QgsPointXY, QgsSpatialIndex,
    QgsVectorFileWriter, QgsCoordinateReferenceSystem
)
from PyQt5.QtCore import QVariant
import processing
import math
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")


def morans_i_manual(layer, field_name, k=8):
    """
    Compute Global Moran's I for spatial autocorrelation.
    Uses k-nearest-neighbors for weight matrix.
    """
    features = list(layer.getFeatures())
    n = len(features)
    values = [f[field_name] for f in features]
    mean_val = sum(values) / n

    centroids = []
    for f in features:
        c = f.geometry().centroid().asPoint()
        centroids.append((c.x(), c.y()))

    spatial_idx = QgsSpatialIndex(layer.getFeatures())

    numerator = 0
    denominator = sum((v - mean_val) ** 2 for v in values)
    w_total = 0

    for i in range(n):
        nearest = spatial_idx.nearestNeighbor(
            QgsPointXY(centroids[i][0], centroids[i][1]), k + 1
        )
        for j_id in nearest:
            if j_id == features[i].id():
                continue
            j_idx = j_id
            if j_idx < n:
                w = 1.0
                numerator += w * (values[i] - mean_val) * (values[j_idx] - mean_val)
                w_total += w

    if denominator == 0 or w_total == 0:
        return 0

    morans = (n / w_total) * (numerator / denominator)
    return round(morans, 4)


def compute_local_density_features(grid_layer, point_layer, field_prefix, radius_deg=0.005):
    """
    For each grid cell, compute density-based features from nearby points.
    Useful for training ML models on spatial context.
    """
    grid_layer.startEditing()

    count_field = QgsField(f"{field_prefix}_count", QVariant.Int)
    mean_field = QgsField(f"{field_prefix}_mean_temp", QVariant.Double)
    std_field = QgsField(f"{field_prefix}_std_temp", QVariant.Double)

    grid_layer.addAttribute(count_field)
    grid_layer.addAttribute(mean_field)
    grid_layer.addAttribute(std_field)
    grid_layer.updateFields()

    count_idx = grid_layer.fields().indexOf(f"{field_prefix}_count")
    mean_idx = grid_layer.fields().indexOf(f"{field_prefix}_mean_temp")
    std_idx = grid_layer.fields().indexOf(f"{field_prefix}_std_temp")

    point_data = []
    for pf in point_layer.getFeatures():
        pt = pf.geometry().asPoint()
        point_data.append((pt.x(), pt.y(), pf["temp_c"]))

    for feature in grid_layer.getFeatures():
        centroid = feature.geometry().centroid().asPoint()
        cx, cy = centroid.x(), centroid.y()

        nearby_temps = []
        for px, py, temp in point_data:
            if abs(px - cx) < radius_deg and abs(py - cy) < radius_deg:
                dist = math.sqrt((px - cx)**2 + (py - cy)**2)
                if dist < radius_deg:
                    nearby_temps.append(temp)

        count = len(nearby_temps)
        mean_temp = sum(nearby_temps) / count if count > 0 else 0
        std_temp = 0
        if count > 1:
            std_temp = math.sqrt(sum((t - mean_temp)**2 for t in nearby_temps) / (count - 1))

        grid_layer.changeAttributeValue(feature.id(), count_idx, count)
        grid_layer.changeAttributeValue(feature.id(), mean_idx, round(mean_temp, 2))
        grid_layer.changeAttributeValue(feature.id(), std_idx, round(std_temp, 3))

    grid_layer.commitChanges()
    print(f"  Local density features computed for '{field_prefix}'.")


def generate_ml_training_dataset(grid_layer):
    """
    Export a clean CSV dataset suitable for machine learning.
    Each row = one grid cell with engineered spatial features.
    """
    output_csv = os.path.join(OUTPUT_DIR, "ml_training_features.csv")

    fields_to_export = [
        "cell_id", "surface_temp_c", "ndvi", "impervious_pct",
        "pop_density_km2", "median_income_usd", "tree_canopy_pct",
        "vulnerability_index", "heat_equity_idx", "green_access_m",
        "sensor_count", "sensor_mean_temp", "sensor_std_temp"
    ]

    available = [f.name() for f in grid_layer.fields()]
    export_fields = [f for f in fields_to_export if f in available]

    with open(output_csv, "w") as f:
        centroid_fields = ["centroid_x", "centroid_y"]
        f.write(",".join(export_fields + centroid_fields) + "\n")

        for feature in grid_layer.getFeatures():
            centroid = feature.geometry().centroid().asPoint()
            values = [str(feature[field]) for field in export_fields]
            values.extend([str(round(centroid.x(), 6)), str(round(centroid.y(), 6))])
            f.write(",".join(values) + "\n")

    print(f"  ML training dataset exported: {output_csv}")
    print(f"  Features: {len(export_fields) + 2} columns, {grid_layer.featureCount()} rows")


def spatial_lag_features(grid_layer, field_name="surface_temp_c"):
    """
    Compute spatial lag (mean of neighboring cells' values) for a given field.
    Critical feature for spatial ML models.
    """
    grid_layer.startEditing()
    lag_field = QgsField(f"{field_name}_spatial_lag", QVariant.Double)
    grid_layer.addAttribute(lag_field)
    grid_layer.updateFields()
    lag_idx = grid_layer.fields().indexOf(f"{field_name}_spatial_lag")

    features = list(grid_layer.getFeatures())
    cell_data = {}
    for f in features:
        row, col = f["row"], f["col"]
        cell_data[(row, col)] = (f.id(), f[field_name])

    for f in features:
        row, col = f["row"], f["col"]
        neighbor_vals = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                key = (row + dr, col + dc)
                if key in cell_data:
                    neighbor_vals.append(cell_data[key][1])

        lag_val = sum(neighbor_vals) / len(neighbor_vals) if neighbor_vals else f[field_name]
        grid_layer.changeAttributeValue(f.id(), lag_idx, round(lag_val, 3))

    grid_layer.commitChanges()
    print(f"  Spatial lag computed for '{field_name}'.")


def run_spatial_statistics():
    """Execute spatial statistics and feature engineering pipeline."""
    print("=" * 60)
    print("SPATIAL STATISTICS & ML FEATURE ENGINEERING")
    print("=" * 60)

    project = QgsProject.instance()
    grid_layer = project.mapLayersByName("Analysis Grid")[0]
    sensor_layer = project.mapLayersByName("Temperature Sensors")[0]

    print("\n[1/4] Computing Global Moran's I...")
    mi_temp = morans_i_manual(grid_layer, "surface_temp_c")
    mi_ndvi = morans_i_manual(grid_layer, "ndvi")
    print(f"  Moran's I (Temperature): {mi_temp}")
    print(f"  Moran's I (NDVI):        {mi_ndvi}")

    print("\n[2/4] Computing local sensor density features...")
    compute_local_density_features(grid_layer, sensor_layer, "sensor")

    print("\n[3/4] Computing spatial lag features...")
    spatial_lag_features(grid_layer, "surface_temp_c")

    print("\n[4/4] Exporting ML training dataset...")
    generate_ml_training_dataset(grid_layer)

    print("\n" + "=" * 60)
    print("SPATIAL STATISTICS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_spatial_statistics()
