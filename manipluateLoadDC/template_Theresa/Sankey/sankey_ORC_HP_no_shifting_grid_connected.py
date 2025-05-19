import re
from pathlib import Path
import plotly.graph_objects as go


# Define flows in a human-readable format
flow_data = """
Electricity (import) 27606.17MWh [27606.17] Electricity consumption 51825.57MWh
Building Integrated Photovoltaics (BIPV) 19827.81MWh [19827.81] Local generation and storage 43973.68MWh
Electricity consumption 51825.57MWh [8911.08] District-level heatpumps 16542.43MWh
District-level PV 6629.62MWh [6629.62] Local generation and storage 43973.68MWh 
Electricity consumption 51825.57MWh [17879.45] Data centre 17164.26MWh
Data centre 17164.26MWh [17164.27] ORC 1544.78MWh 
ORC 1544.78MWh [1544.78] Local generation and storage 43973.68MWh
Electricity consumption 51825.57MWh [7632.61] Data centre heatpump 18661.73MWh
Data centre heatpump 18661.73MWh [18661.73] Heat from DHN 35204.16MWh
Electricity consumption 51825.57MWh [6750.96] Electrical appliances 6750.96MWh
Local generation and storage 43973.68MWh [19751.55] District-level Battery 15971.46MWh 
District-level Battery 15971.46MWh [15971.46] Local generation and storage 43973.68MWh
District-level heatpumps 16542.43MWh [16542.43] Heat from DHN 35204.16MWh
Heat from DHN 35204.16MWh [4261.68] Building level heatpumps 5034.84MWh
Heat from DHN 35204.16MWh [30938.13] Heat exchanger (in) 30938.13MWh
Electricity consumption 51825.57MWh [1470.21] Electrical heater 1440.81MWh
Electrical heater 1440.81MWh [1440.81] Space heating 31921.93MWh
Electricity consumption 51825.57MWh [986.24] Building level heatpumps 5034.84MWh
Building level heatpumps 5034.84MWh [4997.56] Space heating 31921.93MWh
Building level heatpumps 5034.84MWh [37.28] Domestic hot water 851.13MWh
Heat exchanger (in) 30938.13MWh [25483.56] Space heating 31921.93MWh
Heat exchanger (in) 30938.13MWh [813.86] Domestic hot water 851.13MWh 
Local generation and storage 43973.68MWh [23224.01] Electricity consumption 51825.57MWh
Electricity consumption 51825.57MWh [8195.01] Electricity (export) 8195.01MWh
"""


# Define a fixed color mapping for labels to ensure consistent colors across both diagrams
fixed_color_mapping = {
    "Electricity (import) 27606.17MWh": "#1f77b4",
    "Electricity consumption 51825.57MWh": "#ff7f0e",
    "Building Integrated Photovoltaics (BIPV) 19827.81MWh": "#2ca02c",
    "Electricity (export) 8195.01MWh": "#d62728",
    "District-level heatpumps 16542.43MWh": "#9467bd",
    "District-level PV 6629.62MWh": "#8c564b",
    "Data centre 17164.26MWh": "#e377c2",
    "ORC 1544.78MWh": "#bcbd22",
    "Heat exchanger (in) 30938.13MWh": "#17becf",
    "Electrical appliances 6750.96MWh": "#FF5733",
    "District-level Battery 15971.46MWh": "#33FF57",
    "Heat from DHN 35204.16MWh": "#3357FF",
    "Electrical heater 1440.80MWh": "#FF33A1",
    "Space heating 31921.93MWh": "#A133FF",
    "Building level heatpumps 5034.84MWh": "#33FFA1",
    "Domestic hot water 851.13MWh": "#FF5733",
    "Data centre heatpump 18661.73MWh": "#FFD700",
    "Local generation and storage 43973.68MWh": "#FFD700",  # Neue Farbe hinzugefügt
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

    # Define x positions for nodes to move labels to the left side
    node_x_positions = [0.1 if label in ["Electricity (import) 27606.17MWh", "Building Integrated Photovoltaics (BIPV) 19827.81MWh", "District-level PV 6629.62MWh", "Data centre 17164.26MWh", "ORC 1544.78MWh", "Electrical appliances 6750.96MWh", "District-level Battery 15971.46MWh", "District-level heatpumps 16542.43MWh", "Heat from DHN 35204.16MWh", "Electrical heater 1440.80MWh", "Building level heatpumps 5034.84MWh", "Heat exchanger (in) 30938.13MWh", "Local generation and storage 24222.12MWh"] else 0.9 for label in labels]

    # Sankey diagram creation with fixed colors
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors,
            x=node_x_positions  # Set x positions for nodes
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
