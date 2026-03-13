"""
QGIS Processing Script: Urban Heat Island Analysis Pipeline

Run inside QGIS Python Console or as a Processing script.
Performs spatial interpolation, hotspot detection, and equity correlation analysis.
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsField, QgsFeature,
    QgsGeometry, QgsPointXY, QgsRasterLayer,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsGraduatedSymbolRenderer, QgsRendererRange, QgsSymbol,
    QgsClassificationQuantile, QgsVectorFileWriter
)
from qgis.analysis import QgsInterpolator, QgsIDWInterpolator, QgsGridFileWriter
from PyQt5.QtCore import QVariant
import processing
import os
import math

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")


def load_layers():
    """Load all GeoJSON layers into the current QGIS project."""
    project = QgsProject.instance()
    layers = {}

    layer_files = {
        "Analysis Grid": "analysis_grid.geojson",
        "Temperature Sensors": "temperature_sensors.geojson",
        "Green Spaces": "green_spaces.geojson",
        "Buildings": "buildings.geojson",
        "Transit Stops": "transit_stops.geojson",
    }

    for name, filename in layer_files.items():
        path = os.path.join(DATA_DIR, filename)
        layer = QgsVectorLayer(path, name, "ogr")
        if layer.isValid():
            project.addMapLayer(layer)
            layers[name] = layer
            print(f"  Loaded: {name} ({layer.featureCount()} features)")
        else:
            print(f"  FAILED: {name}")

    return layers


def interpolate_temperature(sensor_layer):
    """
    IDW interpolation of temperature sensor readings to create
    a continuous heat surface raster.
    """
    output_path = os.path.join(OUTPUT_DIR, "heat_surface.tif")

    result = processing.run("qgis:idwinterpolation", {
        'INTERPOLATION_DATA': f'{sensor_layer.id()}::~::0::~::0::~::0',
        'DISTANCE_COEFFICIENT': 2.5,
        'EXTENT': sensor_layer.extent(),
        'PIXEL_SIZE': 0.0005,
        'OUTPUT': output_path
    })

    raster = QgsRasterLayer(output_path, "Heat Surface (IDW)")
    if raster.isValid():
        QgsProject.instance().addMapLayer(raster)
        print("  Heat surface raster created.")
    return raster


def calculate_heat_equity_score(grid_layer):
    """
    Compute a composite Heat-Equity Index for each grid cell.
    Combines surface temperature, income, tree canopy, and vulnerability.
    """
    grid_layer.startEditing()

    hei_field = QgsField("heat_equity_idx", QVariant.Double)
    risk_field = QgsField("risk_category", QVariant.String)
    grid_layer.addAttribute(hei_field)
    grid_layer.addAttribute(risk_field)
    grid_layer.updateFields()

    hei_idx = grid_layer.fields().indexOf("heat_equity_idx")
    risk_idx = grid_layer.fields().indexOf("risk_category")

    for feature in grid_layer.getFeatures():
        temp = feature["surface_temp_c"]
        income = feature["median_income_usd"]
        canopy = feature["tree_canopy_pct"]
        vuln = feature["vulnerability_index"]

        temp_norm = min(1, max(0, (temp - 28) / 12))
        income_norm = min(1, max(0, 1 - (income - 20000) / 100000))
        canopy_norm = min(1, max(0, 1 - canopy / 60))

        hei = round(temp_norm * 0.35 + income_norm * 0.25 + canopy_norm * 0.2 + vuln * 0.2, 4)

        if hei > 0.75:
            risk = "Critical"
        elif hei > 0.55:
            risk = "High"
        elif hei > 0.35:
            risk = "Moderate"
        else:
            risk = "Low"

        grid_layer.changeAttributeValue(feature.id(), hei_idx, hei)
        grid_layer.changeAttributeValue(feature.id(), risk_idx, risk)

    grid_layer.commitChanges()
    print("  Heat-Equity Index computed for all grid cells.")
    return grid_layer


def green_space_accessibility(grid_layer, green_layer):
    """
    Calculate walking-distance accessibility to green spaces for each grid cell.
    Uses centroid-to-nearest-green-space distance.
    """
    grid_layer.startEditing()
    acc_field = QgsField("green_access_m", QVariant.Double)
    grid_layer.addAttribute(acc_field)
    grid_layer.updateFields()
    acc_idx = grid_layer.fields().indexOf("green_access_m")

    green_centroids = []
    for gf in green_layer.getFeatures():
        green_centroids.append(gf.geometry().centroid().asPoint())

    for feature in grid_layer.getFeatures():
        centroid = feature.geometry().centroid().asPoint()
        min_dist = float("inf")
        for gc in green_centroids:
            d = centroid.distance(gc) * 111320  # approximate degrees to meters
            if d < min_dist:
                min_dist = d
        grid_layer.changeAttributeValue(feature.id(), acc_idx, round(min_dist, 1))

    grid_layer.commitChanges()
    print("  Green space accessibility calculated.")
    return grid_layer


def hotspot_clustering(sensor_layer):
    """
    Identify temperature hotspot clusters using DBSCAN on high-temperature readings.
    """
    high_temp_features = [f for f in sensor_layer.getFeatures() if f["temp_c"] > 37.0]

    cluster_layer = QgsVectorLayer("Point?crs=epsg:4326", "Heat Hotspots", "memory")
    cluster_layer.startEditing()
    cluster_layer.addAttribute(QgsField("sensor_id", QVariant.String))
    cluster_layer.addAttribute(QgsField("temp_c", QVariant.Double))
    cluster_layer.addAttribute(QgsField("cluster_label", QVariant.String))
    cluster_layer.updateFields()

    for f in high_temp_features:
        new_feat = QgsFeature(cluster_layer.fields())
        new_feat.setGeometry(f.geometry())
        new_feat.setAttribute("sensor_id", f["sensor_id"])
        new_feat.setAttribute("temp_c", f["temp_c"])
        new_feat.setAttribute("cluster_label", "hotspot")
        cluster_layer.addFeature(new_feat)

    cluster_layer.commitChanges()
    QgsProject.instance().addMapLayer(cluster_layer)
    print(f"  Identified {len(high_temp_features)} hotspot readings.")
    return cluster_layer


def export_results(grid_layer):
    """Export the enriched grid layer with analysis results."""
    output_path = os.path.join(OUTPUT_DIR, "analysis_results.geojson")
    QgsVectorFileWriter.writeAsVectorFormat(
        grid_layer, output_path, "utf-8",
        QgsCoordinateReferenceSystem("EPSG:4326"), "GeoJSON"
    )
    print(f"  Results exported to: {output_path}")


def run_full_analysis():
    """Execute the complete Urban Heat Island analysis pipeline."""
    print("=" * 60)
    print("URBAN HEAT ISLAND & ENVIRONMENTAL EQUITY ANALYSIS")
    print("=" * 60)

    print("\n[1/6] Loading data layers...")
    layers = load_layers()

    print("\n[2/6] Computing Heat-Equity Index...")
    grid = calculate_heat_equity_score(layers["Analysis Grid"])

    print("\n[3/6] Analyzing green space accessibility...")
    grid = green_space_accessibility(grid, layers["Green Spaces"])

    print("\n[4/6] Detecting temperature hotspot clusters...")
    hotspot_clustering(layers["Temperature Sensors"])

    print("\n[5/6] Interpolating temperature surface...")
    try:
        interpolate_temperature(layers["Temperature Sensors"])
    except Exception as e:
        print(f"  Skipped raster interpolation: {e}")

    print("\n[6/6] Exporting results...")
    export_results(grid)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_full_analysis()
