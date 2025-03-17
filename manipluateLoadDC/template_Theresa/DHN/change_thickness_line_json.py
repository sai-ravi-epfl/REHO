import json

# Lade die GeoJSON-Datei
with open(r'C:\Users\there\Downloads\test_2.geojson', 'r') as f:
    data = json.load(f)

# Durchlaufe alle Features und setze die Strichstärke basierend auf dem Durchmesser
for feature in data['features']:
    diameter = feature['properties']['diameter']
    stroke_width = diameter * 0.10  # Beispiel: Strichstärke proportional zum Durchmesser
    feature['properties']['stroke-width'] = stroke_width

# Speichere die bearbeitete GeoJSON-Datei
with open(r'C:\Users\there\Downloads\bearbeitete_datei.geojson', 'w') as f:
    json.dump(data, f)