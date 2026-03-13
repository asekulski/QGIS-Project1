"""
QGIS Project Builder: Creates and configures the .qgz project file.
Run this from the QGIS Python Console after opening a blank project.

Usage in QGIS Python Console:
    exec(open('C:/Users/alex/Downloads/urban-heat-equity-qgis/scripts/create_qgis_project.py').read())
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRasterLayer,
    QgsCoordinateReferenceSystem, QgsRectangle,
    QgsGraduatedSymbolRenderer, QgsRendererRange,
    QgsSymbol, QgsSimpleFillSymbolLayer, QgsSimpleMarkerSymbolLayer,
    QgsCategorizedSymbolRenderer, QgsRendererCategory,
    QgsLayerTreeGroup
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QVariant
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
STYLES_DIR = os.path.join(PROJECT_ROOT, "styles")

project = QgsProject.instance()
project.clear()
project.setTitle("Urban Heat Island & Environmental Equity Analysis")
project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

root = project.layerTreeRoot()


def make_graduated_fill(layer, field, ranges_config):
    """Apply graduated color fill renderer."""
    ranges = []
    for lower, upper, color, label in ranges_config:
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        sym_layer = symbol.symbolLayer(0)
        sym_layer.setColor(QColor(*color))
        sym_layer.setStrokeColor(QColor(60, 60, 60, 100))
        sym_layer.setStrokeWidth(0.15)
        ranges.append(QgsRendererRange(lower, upper, symbol, label))
    renderer = QgsGraduatedSymbolRenderer(field, ranges)
    layer.setRenderer(renderer)


def make_categorized_fill(layer, field, categories_config):
    """Apply categorized color fill renderer."""
    cats = []
    for value, color, label in categories_config:
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        sym_layer = symbol.symbolLayer(0)
        sym_layer.setColor(QColor(*color))
        sym_layer.setStrokeColor(QColor(80, 80, 80, 120))
        sym_layer.setStrokeWidth(0.2)
        cats.append(QgsRendererCategory(value, symbol, label))
    renderer = QgsCategorizedSymbolRenderer(field, cats)
    layer.setRenderer(renderer)


def make_graduated_point(layer, field, ranges_config, size_range=(3, 10)):
    """Apply graduated sized+colored point renderer."""
    ranges = []
    n = len(ranges_config)
    for i, (lower, upper, color, label) in enumerate(ranges_config):
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        sym_layer = symbol.symbolLayer(0)
        sym_layer.setColor(QColor(*color))
        sym_layer.setStrokeColor(QColor(40, 40, 40, 180))
        sym_layer.setStrokeWidth(0.3)
        size = size_range[0] + (size_range[1] - size_range[0]) * (i / max(1, n - 1))
        sym_layer.setSize(size)
        ranges.append(QgsRendererRange(lower, upper, symbol, label))
    renderer = QgsGraduatedSymbolRenderer(field, ranges)
    layer.setRenderer(renderer)


# --- Load and Style Layers ---

# 1. Analysis Grid - Heat Map
grid_path = os.path.join(DATA_DIR, "analysis_grid.geojson")
grid_layer = QgsVectorLayer(grid_path, "Surface Temperature Grid", "ogr")
make_graduated_fill(grid_layer, "surface_temp_c", [
    (28, 31, (49, 54, 149, 180), "28-31°C (Cool)"),
    (31, 33, (116, 173, 209, 180), "31-33°C (Mild)"),
    (33, 35, (254, 224, 144, 180), "33-35°C (Warm)"),
    (35, 37, (253, 174, 97, 200), "35-37°C (Hot)"),
    (37, 42, (215, 48, 39, 220), "37-42°C (Extreme)"),
])
project.addMapLayer(grid_layer, False)

# Duplicate grid for vulnerability view
vuln_layer = QgsVectorLayer(grid_path, "Vulnerability Index", "ogr")
make_graduated_fill(vuln_layer, "vulnerability_index", [
    (0, 0.25, (26, 150, 65, 180), "Low"),
    (0.25, 0.45, (166, 217, 106, 180), "Moderate"),
    (0.45, 0.65, (253, 174, 97, 200), "High"),
    (0.65, 1.0, (215, 25, 28, 220), "Critical"),
])
project.addMapLayer(vuln_layer, False)

# Land use grid
lu_layer = QgsVectorLayer(grid_path, "Land Use Classification", "ogr")
make_categorized_fill(lu_layer, "land_use", [
    ("commercial", (220, 50, 50, 180), "Commercial"),
    ("residential_high", (180, 120, 60, 180), "Residential (High Density)"),
    ("residential_low", (255, 220, 150, 180), "Residential (Low Density)"),
    ("industrial", (160, 60, 160, 180), "Industrial"),
    ("park", (50, 180, 50, 180), "Park / Green"),
    ("mixed_use", (60, 130, 200, 180), "Mixed Use"),
    ("institutional", (200, 200, 200, 180), "Institutional"),
])
project.addMapLayer(lu_layer, False)

# 2. Temperature Sensors
sensor_path = os.path.join(DATA_DIR, "temperature_sensors.geojson")
sensor_layer = QgsVectorLayer(sensor_path, "Temperature Sensors", "ogr")
make_graduated_point(sensor_layer, "temp_c", [
    (28, 32, (69, 117, 180, 200), "28-32°C"),
    (32, 35, (254, 224, 144, 200), "32-35°C"),
    (35, 37, (253, 174, 97, 220), "35-37°C"),
    (37, 42, (215, 48, 39, 240), "37-42°C"),
], size_range=(2.5, 5.5))
project.addMapLayer(sensor_layer, False)

# 3. Green Spaces
green_path = os.path.join(DATA_DIR, "green_spaces.geojson")
green_layer = QgsVectorLayer(green_path, "Green Spaces", "ogr")
symbol = QgsSymbol.defaultSymbol(green_layer.geometryType())
sl = symbol.symbolLayer(0)
sl.setColor(QColor(34, 139, 34, 160))
sl.setStrokeColor(QColor(0, 100, 0, 200))
sl.setStrokeWidth(0.5)
green_layer.setRenderer(QgsGraduatedSymbolRenderer.__new__(QgsGraduatedSymbolRenderer) if False else type(green_layer.renderer())(green_layer.renderer()))
from qgis.core import QgsSingleSymbolRenderer
green_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
project.addMapLayer(green_layer, False)

# 4. Buildings
bldg_path = os.path.join(DATA_DIR, "buildings.geojson")
bldg_layer = QgsVectorLayer(bldg_path, "Buildings", "ogr")
make_graduated_fill(bldg_layer, "height_m", [
    (3, 10, (200, 200, 200, 160), "1-3 floors"),
    (10, 28, (170, 170, 190, 180), "3-8 floors"),
    (28, 60, (120, 120, 160, 200), "8-17 floors"),
    (60, 130, (80, 80, 140, 220), "17+ floors"),
])
project.addMapLayer(bldg_layer, False)

# 5. Transit Stops
transit_path = os.path.join(DATA_DIR, "transit_stops.geojson")
transit_layer = QgsVectorLayer(transit_path, "Transit Stops (Heat Exposure)", "ogr")
make_graduated_point(transit_layer, "heat_exposure_score", [
    (0, 0.3, (26, 150, 65, 200), "Low Exposure"),
    (0.3, 0.5, (255, 255, 100, 200), "Moderate"),
    (0.5, 0.7, (253, 174, 97, 220), "High"),
    (0.7, 1.0, (215, 48, 39, 240), "Extreme"),
], size_range=(3, 7))
project.addMapLayer(transit_layer, False)


# --- Organize Layer Tree ---
heat_group = root.addGroup("Heat Analysis")
heat_group.addLayer(grid_layer)
heat_group.addLayer(sensor_layer)

equity_group = root.addGroup("Equity & Demographics")
equity_group.addLayer(vuln_layer)
equity_group.addLayer(lu_layer)

infra_group = root.addGroup("Infrastructure")
infra_group.addLayer(bldg_layer)
infra_group.addLayer(green_layer)
infra_group.addLayer(transit_layer)

# Set some layers invisible by default to reduce clutter
vuln_layer_node = root.findLayer(vuln_layer.id())
if vuln_layer_node:
    vuln_layer_node.setItemVisibilityChecked(False)
lu_node = root.findLayer(lu_layer.id())
if lu_node:
    lu_node.setItemVisibilityChecked(False)
bldg_node = root.findLayer(bldg_layer.id())
if bldg_node:
    bldg_node.setItemVisibilityChecked(False)

# Set map extent
project.viewSettings().setDefaultViewExtent(
    QgsRectangle(-97.80, 30.22, -97.69, 30.32)
)

# Save project
project_path = os.path.join(PROJECT_ROOT, "urban_heat_equity.qgz")
project.write(project_path)
print(f"\nProject saved to: {project_path}")
print("Open this file in QGIS to view the fully styled project.")
