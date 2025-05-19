import re
from pathlib import Path
import plotly.graph_objects as go


# Define flows in a human-readable format
flow_data = """
Electricity (import) 25054.72MWh [25054.72] Electricity consumption 48276.01MWh
Building Integrated Photovoltaics (BIPV) 19827.81MWh [19827.81] Local generation and storage 42655.37MWh
Electricity consumption 48276.01MWh [12602.01] District-level heatpumps 23394.22MWh
District-level PV 6632.22MWh [6632.22] Local generation and storage 42655.37MWh 
Electricity consumption 48276.01MWh [17892.50] Data centre 17176.81MWh
Data centre 17176.81MWh [5366.87] ORC 483.02MWh 
Data centre 17176.81MWh [11809.94] Heat from DHN 35204.16MWh
ORC 483.02MWh [483.02] Local generation and storage 42655.37MWh
Electricity consumption 48276.01MWh [6750.96] Electrical appliances 6750.96MWh
Local generation and storage 42655.37MWh [19431.35] District-level Battery 15712.32MWh 
District-level Battery 15712.32MWh [15712.32] Local generation and storage 42655.37MWh
District-level heatpumps 23394.22MWh [23394.22] Heat from DHN 35204.16MWh
Heat from DHN 35204.16MWh [4261.68] Building level heatpumps 5034.84MWh
Heat from DHN 35204.16MWh [30938.13] Heat exchanger (in) 30938.13MWh
Electricity consumption 48276.01MWh [1470.21] Electrical heater 1440.81MWh
Electrical heater 1440.81MWh [1440.81] Space heating 31921.93MWh
Electricity consumption 48276.01MWh [986.24] Building level heatpumps 5034.84MWh
Building level heatpumps 5034.84MWh [4997.56] Space heating 31921.93MWh
Building level heatpumps 5034.84MWh [37.28] Domestic hot water 851.13MWh
Heat exchanger (in) 30938.13MWh [25483.56] Space heating 31921.93MWh
Heat exchanger (in) 30938.13MWh [813.86] Domestic hot water 851.13MWh 
Local generation and storage 42655.37MWh [23224.01] Electricity consumption 48276.01MWh
Electricity consumption 48276.01MWh [8574.08] Electricity (export) 8574.08MWh
"""


# Define a fixed color mapping for labels to ensure consistent colors across both diagrams, including the number from the units/nodes in the color mapping
fixed_color_mapping = {
    "Electricity (import) 25054.72MWh": "#1f77b4",
    "Electricity consumption 48276.01MWh": "#ff7f0e",
    "Building Integrated Photovoltaics (BIPV) 19827.81MWh": "#2ca02c",
    "Electricity (export) 8574.08MWh": "#d62728",
    "District-level heatpumps 23394.22MWh": "#9467bd",
    "District-level PV 6632.22MWh": "#8c564b",
    "Data centre 17176.81MWh": "#e377c2",
    "ORC 483.02MWh": "#bcbd22",
    "Heat exchanger (in) 30938.13MWh": "#17becf",
    "Electrical appliances 6750.96MWh": "#FF5733",
    "District-level Battery 15712.32MWh": "#33FF57",
    "Heat from DHN 35204.16MWh": "#3357FF",
    "Electrical heater 1440.81MWh": "#FF33A1",
    "Space heating 31921.93MWh": "#A133FF",
    "Building level heatpumps 5034.84MWh": "#33FFA1",
    "Domestic hot water 851.13MWh": "#FF5733",
    "Local generation and storage 42655.37MWh": "#FFD700",  # Neue Farbe hinzugefügt
}

def create_sankey_diagram(flow_data, fixed_color_mapping):
    # Parse the flows
    sources = []
    targets = []
    values = []
    labels = set()  # To ensure unique node labels

    for line in flow_data.strip().split("\n"):
        match = re.match(r"(.+?) \[(\d+(\.\d+)?)] (.+)", line)
        if match:
            source, value, _, target = match.groups()
            sources.append(source.strip())
            targets.append(target.strip())
            values.append(float(value))
            labels.update([source.strip(), target.strip()])
        else:
            raise ValueError(f"Invalid format in line: {line}")

    # Create label-to-index mapping
    labels = list(labels)
    label_to_index = {label: i for i, label in enumerate(labels)}

    # Convert sources and targets to indices
    source_indices = [label_to_index[source] for source in sources]
    target_indices = [label_to_index[target] for target in targets]

    # Assign colors to nodes based on the fixed color mapping, use a default color if the label is not in the mapping
    node_colors = [fixed_color_mapping.get(label, "#000000") for label in labels]

    # Sankey diagram creation with fixed colors
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors,
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color="rgba(150, 150, 150, 0.4)"  # Uniform gray links
        )
    ))


    # Update layout for aesthetics
    fig.update_layout(
        font=dict(size=14, family="Arial"),
        title_font=dict(size=16, family="Arial", color="black"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=50, t=50, b=50),
        height=600,
        width=900
    )

    # Show figure
    fig.show()

# Create the Sankey diagram with the provided flow data and fixed color mapping
create_sankey_diagram(flow_data, fixed_color_mapping)