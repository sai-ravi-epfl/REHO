import re
from pathlib import Path
import plotly.graph_objects as go


# Define flows in a human-readable format
flow_data = """
Electricity (import) 20739.18MWh [20739.18] Electricity consumption 45105.24MWh
Building Integrated Photovoltaics (BIPV) 19804.06MWh [19804.06] Local generation and storage 34704.92MWh
Electricity consumption 45105.24MWh [10479.18] District-level heatpumps 19453.43MWh
District-level PV 5409.83MWh [5409.83] Local generation and storage 34704.92MWh 
Electricity consumption 45105.24MWh [13086.59] Data centre 12563.13MWh
Data centre 12563.13MWh [12563.13] ORC 1130.68MWh 
ORC 1130.68MWh [1130.68] Local generation and storage 34704.92MWh
Electricity consumption 45105.24MWh [5796.82] Data centre heatpump 14173.22MWh
Data centre heatpump 14173.22MWh [14173.22] Heat from DHN 33626.65MWh
Electricity consumption 45105.24MWh [7368.81] Electrical appliances 7368.81MWh
Local generation and storage 34704.92MWh [10336.44] District-level Battery 8360.35MWh 
District-level Battery 8360.35MWh [8360.35] Local generation and storage 34704.92MWh
District-level heatpumps 19453.43MWh [19453.43] Heat from DHN 33626.65MWh
Heat from DHN 33626.65MWh [7536.09] Building level heatpumps 9162.78MWh
Heat from DHN 33626.65MWh [30938.13] Heat exchanger (in) 26085.94MWh
Electricity consumption 45105.24MWh [778.50] Electrical heater 762.93MWh
Electrical heater 762.93MWh [762.93] Space heating 31191.91MWh
Electricity consumption 45105.24MWh [2003.50] Building level heatpumps 9162.78MWh
Building level heatpumps 9162.78MWh [9034.37] Space heating 31191.91MWh
Building level heatpumps 9162.78MWh [128.41] Domestic hot water 906.24MWh
Heat exchanger (in) 26085.94MWh [21395.21] Space heating 31191.91MWh
Heat exchanger (in) 26085.94MWh [777.83] Domestic hot water 906.24MWh 
Local generation and storage 34704.92MWh [23224.01] Electricity consumption 45105.24MWh
Electricity consumption 45105.24MWh [5591.84] Electricity (export) 5591.84MWh
"""


# Define a fixed color mapping for labels to ensure consistent colors across both diagrams

fixed_color_mapping = {
     "Electricity (import) 20739.18MWh": "#1f77b4",
     "Electricity consumption 45105.24MWh": "#ff7f0e",
     "Building Integrated Photovoltaics (BIPV) 19804.06MWh": "#2ca02c",
     "Electricity (export) 5591.84MWh": "#d62728",
     "District-level heatpumps 19453.43MWh": "#9467bd",
     "District-level PV 5409.83MWh": "#8c564b",
     "Data centre 12563.13MWh": "#e377c2",
     "ORC 1130.68MWh": "#bcbd22",
     "Heat exchanger (in) 26085.94MWh": "#17becf",
     "Electrical appliances 7368.81MWh": "#FF5733",
     "District-level Battery 8360.35MWh": "#33FF57",
     "Heat from DHN 33626.65MWh": "#3357FF",
     "Electrical heater 762.93MWh": "#FF33A1",
     "Space heating 31191.91MWh": "#A133FF",
     "Building level heatpumps 9162.78MWh": "#33FFA1",
     "Domestic hot water 906.24MWh": "#FF5733",
     "Data centre heatpump 14173.22MWh": "#FFD700",
     "Local generation and storage 34704.92MWh": "#FFD700", # Neue Farbe hinzugefügt
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
            color=node_colors
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