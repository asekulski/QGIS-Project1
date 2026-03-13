"""
Synthetic Geodata Generator for Urban Heat Island & Environmental Equity Analysis.
Generates realistic GeoJSON layers for a fictional metro area based on Austin, TX coordinates.
"""

import json
import math
import random
import os

random.seed(42)

CENTER_LAT = 30.2672
CENTER_LON = -97.7431
CITY_NAME = "Metro Austin Study Area"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def offset(lat, lon, d_north_m, d_east_m):
    new_lat = lat + (d_north_m / 111320)
    new_lon = lon + (d_east_m / (111320 * math.cos(math.radians(lat))))
    return round(new_lat, 6), round(new_lon, 6)


def make_rect(center_lat, center_lon, w_m, h_m):
    hw, hh = w_m / 2, h_m / 2
    nw = offset(center_lat, center_lon, hh, -hw)
    ne = offset(center_lat, center_lon, hh, hw)
    se = offset(center_lat, center_lon, -hh, hw)
    sw = offset(center_lat, center_lon, -hh, -hw)
    return [[nw[1], nw[0]], [ne[1], ne[0]], [se[1], se[0]], [sw[1], sw[0]], [nw[1], nw[0]]]


def generate_grid_cells():
    """Generate a 20x20 grid of analysis cells across the study area."""
    features = []
    cell_size = 500  # meters
    grid_n = 20
    total_span = cell_size * grid_n

    for row in range(grid_n):
        for col in range(grid_n):
            d_north = (row - grid_n / 2) * cell_size + cell_size / 2
            d_east = (col - grid_n / 2) * cell_size + cell_size / 2
            clat, clon = offset(CENTER_LAT, CENTER_LON, d_north, d_east)

            dist_from_center = math.sqrt(d_north**2 + d_east**2)
            norm_dist = dist_from_center / (total_span / 2)

            base_temp = 38.5 - 4.5 * norm_dist + random.gauss(0, 1.2)
            ndvi = 0.15 + 0.45 * norm_dist + random.gauss(0, 0.08)
            ndvi = max(0.05, min(0.85, ndvi))
            impervious_pct = max(5, min(98, 85 - 60 * norm_dist + random.gauss(0, 8)))

            land_uses = ["commercial", "residential_high", "residential_low",
                         "industrial", "park", "mixed_use", "institutional"]
            if norm_dist < 0.3:
                weights = [35, 15, 2, 10, 3, 30, 5]
            elif norm_dist < 0.6:
                weights = [10, 30, 20, 8, 10, 15, 7]
            else:
                weights = [3, 10, 45, 5, 20, 5, 12]
            land_use = random.choices(land_uses, weights=weights, k=1)[0]

            if land_use == "park":
                base_temp -= random.uniform(1.5, 3.5)
                ndvi = min(0.85, ndvi + random.uniform(0.15, 0.3))
                impervious_pct = max(5, impervious_pct - 40)
            elif land_use == "industrial":
                base_temp += random.uniform(1.0, 2.5)
                ndvi = max(0.05, ndvi - 0.1)

            pop_density = max(50, int(3000 * (1 - norm_dist * 0.6) + random.gauss(0, 400)))
            median_income = max(22000, int(45000 + 55000 * norm_dist * random.uniform(0.3, 1.5) + random.gauss(0, 8000)))
            tree_canopy_pct = max(2, min(65, ndvi * 70 + random.gauss(0, 5)))
            vulnerability_idx = round(max(0, min(1,
                (base_temp - 30) / 12 * 0.4 +
                (1 - median_income / 120000) * 0.3 +
                (1 - tree_canopy_pct / 65) * 0.3
            )), 3)

            coords = make_rect(clat, clon, cell_size, cell_size)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [coords]},
                "properties": {
                    "cell_id": f"C{row:02d}{col:02d}",
                    "surface_temp_c": round(base_temp, 2),
                    "ndvi": round(ndvi, 3),
                    "impervious_pct": round(impervious_pct, 1),
                    "land_use": land_use,
                    "pop_density_km2": pop_density,
                    "median_income_usd": median_income,
                    "tree_canopy_pct": round(tree_canopy_pct, 1),
                    "vulnerability_index": vulnerability_idx,
                    "row": row,
                    "col": col
                }
            })

    return {"type": "FeatureCollection", "name": "analysis_grid", "features": features}


def generate_temperature_points():
    """Generate 300 temperature sensor readings scattered across the study area."""
    features = []
    for i in range(300):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, 5000)
        d_north = radius * math.cos(angle)
        d_east = radius * math.sin(angle)
        lat, lon = offset(CENTER_LAT, CENTER_LON, d_north, d_east)

        dist = math.sqrt(d_north**2 + d_east**2) / 5000
        temp = 38.5 - 5 * dist + random.gauss(0, 1.8)
        humidity = 35 + 25 * dist + random.gauss(0, 5)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "sensor_id": f"S{i:03d}",
                "temp_c": round(temp, 2),
                "humidity_pct": round(max(20, min(90, humidity)), 1),
                "measurement_date": "2025-07-15",
                "measurement_time": f"{random.randint(12,15):02d}:{random.randint(0,59):02d}",
                "sensor_type": random.choice(["ground_station", "mobile", "rooftop", "satellite_derived"]),
                "elevation_m": round(150 + random.gauss(0, 20), 1)
            }
        })

    return {"type": "FeatureCollection", "name": "temperature_sensors", "features": features}


def generate_green_spaces():
    """Generate 45 parks and green spaces as polygons."""
    features = []
    park_names = [
        "Zilker Park", "Pease Park", "Mueller Greenway", "Shoal Creek Greenbelt",
        "Lady Bird Lake Trail", "Barton Springs", "McKinney Falls", "Bull Creek Park",
        "Walnut Creek Metro", "Emma Long Park", "Commons Ford Ranch",
        "Roy Guerrero Park", "Onion Creek Metro", "Mary Moore Searight",
        "Circle C Ranch Park", "Bartholomew Park", "Givens District Park",
        "Patterson Park", "Dove Springs Rec", "St. Edwards Greenbelt",
    ]
    for i in range(45):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(500, 5500)
        d_north = radius * math.cos(angle)
        d_east = radius * math.sin(angle)
        clat, clon = offset(CENTER_LAT, CENTER_LON, d_north, d_east)

        park_w = random.uniform(80, 600)
        park_h = random.uniform(80, 600)
        area_ha = round((park_w * park_h) / 10000, 2)
        coords = make_rect(clat, clon, park_w, park_h)

        name = park_names[i] if i < len(park_names) else f"Community Green #{i}"
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {
                "park_id": f"P{i:03d}",
                "name": name,
                "area_ha": area_ha,
                "tree_density": random.choice(["sparse", "moderate", "dense"]),
                "has_water_feature": random.choice([True, False]),
                "cooling_effect_radius_m": int(park_w * random.uniform(1.5, 3.0)),
                "avg_temp_reduction_c": round(random.uniform(0.8, 3.5), 2),
                "accessibility_score": round(random.uniform(0.3, 1.0), 2)
            }
        })

    return {"type": "FeatureCollection", "name": "green_spaces", "features": features}


def generate_buildings():
    """Generate 500 building footprints."""
    features = []
    for i in range(500):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(50, 5200)
        d_north = radius * math.cos(angle)
        d_east = radius * math.sin(angle)
        clat, clon = offset(CENTER_LAT, CENTER_LON, d_north, d_east)

        dist = radius / 5200
        if dist < 0.25:
            w = random.uniform(30, 100)
            h = random.uniform(30, 100)
            floors = random.randint(5, 35)
            btype = random.choice(["office", "commercial", "mixed_use", "hotel"])
            material = random.choice(["glass_steel", "concrete", "stone_facade"])
        elif dist < 0.55:
            w = random.uniform(15, 50)
            h = random.uniform(15, 50)
            floors = random.randint(2, 8)
            btype = random.choice(["residential", "retail", "office", "apartment"])
            material = random.choice(["brick", "concrete", "stucco"])
        else:
            w = random.uniform(10, 30)
            h = random.uniform(10, 30)
            floors = random.randint(1, 3)
            btype = random.choice(["residential", "single_family", "retail", "warehouse"])
            material = random.choice(["wood_frame", "brick", "vinyl_siding"])

        albedo = {"glass_steel": 0.25, "concrete": 0.35, "stone_facade": 0.4,
                  "brick": 0.3, "stucco": 0.45, "wood_frame": 0.4, "vinyl_siding": 0.5}
        has_green_roof = random.random() < (0.15 if dist < 0.3 else 0.03)

        coords = make_rect(clat, clon, w, h)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {
                "bld_id": f"B{i:04d}",
                "building_type": btype,
                "floors": floors,
                "height_m": round(floors * 3.5, 1),
                "footprint_m2": round(w * h, 1),
                "material": material,
                "albedo": albedo.get(material, 0.35),
                "has_green_roof": has_green_roof,
                "year_built": random.randint(1960, 2024),
                "energy_rating": random.choice(["A", "B", "C", "D", "E"])
            }
        })

    return {"type": "FeatureCollection", "name": "buildings", "features": features}


def generate_transit_stops():
    """Generate 80 transit stop points."""
    features = []
    for i in range(80):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(200, 5000)
        d_north = radius * math.cos(angle)
        d_east = radius * math.sin(angle)
        lat, lon = offset(CENTER_LAT, CENTER_LON, d_north, d_east)

        dist = radius / 5000
        has_shade = random.random() < (0.6 if dist < 0.4 else 0.25)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "stop_id": f"T{i:03d}",
                "stop_name": f"Stop {i+1}",
                "route_type": random.choice(["bus", "bus_rapid", "rail", "shuttle"]),
                "daily_ridership": random.randint(50, 5000),
                "has_shade_structure": has_shade,
                "has_cooling_station": random.random() < 0.1,
                "heat_exposure_score": round(max(0, min(1, 0.3 + 0.5 * (1 - dist) + random.gauss(0, 0.12))), 3)
            }
        })

    return {"type": "FeatureCollection", "name": "transit_stops", "features": features}


def save_geojson(data, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  -> {filename} ({len(data['features'])} features)")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating Urban Heat Island study data...\n")

    save_geojson(generate_grid_cells(), "analysis_grid.geojson")
    save_geojson(generate_temperature_points(), "temperature_sensors.geojson")
    save_geojson(generate_green_spaces(), "green_spaces.geojson")
    save_geojson(generate_buildings(), "buildings.geojson")
    save_geojson(generate_transit_stops(), "transit_stops.geojson")

    print("\nAll layers generated successfully.")
