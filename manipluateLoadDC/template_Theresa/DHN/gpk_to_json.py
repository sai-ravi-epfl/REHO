import geopandas as gpd
import json
from shapely.geometry import mapping, MultiLineString, LineString

# Custom function to convert geometries to a serializable format
def geometry_to_geojson(geometry):
    if isinstance(geometry, (MultiLineString, LineString)):
        return mapping(geometry)
    return mapping(geometry)

# Load the GeoPackage file
gdf = gpd.read_file(r'C:\Users\there\Downloads\EPFL_1_EPFL_70_60_water_02_Q_peak_1.5_gurobi_simplified_tree_diameter.gpkg')

# Add stroke width based on the diameter
features = []
for _, row in gdf.iterrows():
    feature = {
        "type": "Feature",
        "geometry": geometry_to_geojson(row.geometry),  # Convert geometry to a serializable format
        "properties": row.to_dict()
    }
    diameter = row['diameter']  # Assumption: Diameter is stored in the properties
    feature['properties']['stroke-width'] = diameter * 10  # Adjust the factor as needed
    features.append(feature)

# Create the GeoJSON data format
geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Custom JSON encoder to handle MultiLineString objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (MultiLineString, LineString)):
            return mapping(obj)
        return super().default(obj)

# Save the modified GeoJSON file
with open('output_file_with_stroke.geojson', 'w') as f:
    json.dump(geojson_data, f, cls=CustomJSONEncoder)