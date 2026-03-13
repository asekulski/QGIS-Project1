# Urban Heat Island & Environmental Equity Analysis

A comprehensive QGIS geospatial analysis project that examines the intersection of urban heat island intensity and socioeconomic vulnerability across a metropolitan study area. Designed to demonstrate advanced geospatial analysis, spatial statistics, and AI-ready feature engineering skills.

## Project Overview

| Component | Details |
|-----------|---------|
| **Study Area** | Metro Austin, TX (10km x 10km grid) |
| **Grid Resolution** | 500m cells (20x20 = 400 cells) |
| **Data Layers** | 5 vector layers, 1,325 total features |
| **Analysis Scripts** | 3 Python processing pipelines |
| **Output** | Styled QGIS project + Interactive web map |

## Data Layers

| Layer | Features | Type | Key Attributes |
|-------|----------|------|----------------|
| Analysis Grid | 400 | Polygon | Surface temp, NDVI, impervious %, land use, demographics, vulnerability index |
| Temperature Sensors | 300 | Point | Temp readings, humidity, sensor type, elevation |
| Green Spaces | 45 | Polygon | Area, tree density, cooling effect radius, accessibility score |
| Buildings | 500 | Polygon | Height, material, albedo, green roof status, energy rating |
| Transit Stops | 80 | Point | Ridership, shade infrastructure, heat exposure score |

## Analysis Pipeline

### 1. Heat-Equity Index (HEI)
Composite vulnerability metric combining:
- **35%** Surface temperature (normalized)
- **25%** Income disparity
- **20%** Tree canopy deficit
- **20%** Vulnerability index

### 2. IDW Temperature Interpolation
Inverse Distance Weighted interpolation of 300 sensor readings to produce a continuous heat surface raster.

### 3. Spatial Autocorrelation
Global Moran's I computed for temperature and NDVI fields to quantify spatial clustering patterns.

### 4. ML Feature Engineering
- Spatial lag computation (neighbor-averaged values)
- Local density statistics (count, mean, std of nearby sensors)
- Green space accessibility (nearest-park distance)
- Export to training-ready CSV for predictive modeling

## Quick Start

### Prerequisites
- **QGIS 3.28+** (LTR recommended) — [Download](https://qgis.org/download/)
- **Python 3.9+** (bundled with QGIS)

### Step 1: Generate Data
The data has already been generated in `/data/`. To regenerate:
```
python scripts/generate_data.py
```

### Step 2: Open in QGIS (Option A — Automated)
1. Open QGIS
2. Open the **Python Console** (Plugins → Python Console)
3. Run:
```python
exec(open('C:/Users/alex/Downloads/urban-heat-equity-qgis/scripts/create_qgis_project.py').read())
```
4. This loads all layers with full styling and saves `urban_heat_equity.qgz`

### Step 2: Open in QGIS (Option B — Manual)
1. Open QGIS → New Project
2. Layer → Add Layer → Add Vector Layer
3. Browse to `/data/` and add each `.geojson` file
4. Right-click each layer → Properties → Symbology to apply styles from `/styles/`

### Step 3: Run Analysis
In the QGIS Python Console:
```python
exec(open('C:/Users/alex/Downloads/urban-heat-equity-qgis/scripts/heat_island_analysis.py').read())
```
Then for spatial statistics and ML feature export:
```python
exec(open('C:/Users/alex/Downloads/urban-heat-equity-qgis/scripts/spatial_statistics.py').read())
```

### Step 4: View the Web Map
See the **Web Hosting** section below.

## Web Hosting (Portfolio Display)

### Local Preview
Start a local web server from the project root:

```bash
# Python (simplest)
cd urban-heat-equity-qgis
python -m http.server 8000

# Then open: http://localhost:8000/web/
```

### Deploy to GitHub Pages (Free)
1. Create a GitHub repository
2. Push the entire project:
```bash
cd urban-heat-equity-qgis
git init
git add .
git commit -m "Urban Heat Island QGIS analysis project"
git remote add origin https://github.com/YOUR_USERNAME/urban-heat-equity-qgis.git
git push -u origin main
```
3. Go to repository **Settings → Pages**
4. Set Source to `main` branch, folder `/` (root)
5. Your web map will be live at: `https://YOUR_USERNAME.github.io/urban-heat-equity-qgis/web/`

### Deploy to Netlify (Free)
1. Go to [netlify.com](https://netlify.com) and sign in
2. Drag and drop the entire `urban-heat-equity-qgis` folder
3. Your site is live instantly with a custom URL

### Deploy to Vercel (Free)
```bash
npm i -g vercel
cd urban-heat-equity-qgis
vercel
```

## Project Structure

```
urban-heat-equity-qgis/
├── README.md
├── data/
│   ├── analysis_grid.geojson      # 400-cell analysis grid
│   ├── temperature_sensors.geojson # 300 sensor readings
│   ├── green_spaces.geojson       # 45 parks & green areas
│   ├── buildings.geojson          # 500 building footprints
│   └── transit_stops.geojson      # 80 transit stops
├── scripts/
│   ├── generate_data.py           # Synthetic data generator
│   ├── create_qgis_project.py     # Automated QGIS project builder
│   ├── heat_island_analysis.py    # Core UHI analysis pipeline
│   └── spatial_statistics.py      # Spatial stats & ML features
├── styles/
│   ├── heat_grid.qml              # Temperature graduated style
│   └── vulnerability.qml          # Vulnerability graduated style
├── web/
│   └── index.html                 # Interactive Leaflet web map
└── output/                        # Generated analysis results
```

## Technologies

- **QGIS 3.34** — Desktop GIS platform
- **PyQGIS** — Python bindings for QGIS API
- **QGIS Processing** — Geoprocessing framework (IDW, spatial joins)
- **Leaflet.js** — Interactive web map library
- **GeoJSON** — Open standard geospatial data format
- **Python** — Data generation, analysis, feature engineering

## Key Skills Demonstrated

- Vector & raster geospatial analysis
- Spatial interpolation (IDW)
- Spatial statistics (Moran's I, spatial autocorrelation)
- Custom QGIS Processing algorithms
- Cartographic styling & layer management
- Web map development (Leaflet.js)
- AI/ML-ready geospatial feature engineering
- Geodata generation & quality control
- Environmental equity & urban planning analysis
