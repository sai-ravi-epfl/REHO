import re
from pathlib import Path
import plotly.graph_objects as go


# Define flows in a human-readable format
flow_data = """
Electricity (import) 18996.44MWh [18996.44] Electricity consumption 42423.69MWh
Building Integrated Photovoltaics (BIPV) 19804.06MWh [19804.06] Local generation and storage 34350.95MWh
Electricity consumption 42423.69MWh [13312.78] District-level heatpumps 24713.70MWh
District-level PV 5386.41MWh [5386.41] Local generation and storage 34350.95MWh 
Electricity consumption 42423.69MWh [13069.09] Data centre 12546.32MWh
Data centre 12546.32MWh [3633.38] ORC 327.00MWh 
Data centre 12546.32MWh [8912.95] Heat from DHN 33626.65MWh
ORC 327.00MWh [327.00] Local generation and storage 34350.95MWh
Electricity consumption 42423.69MWh [7368.81] Electrical appliances 7368.81MWh
Local generation and storage 34350.95MWh [10921.28] District-level Battery 8833.47MWh 
District-level Battery 8833.47MWh [8833.47] Local generation and storage 34350.95MWh
District-level heatpumps 24713.70MWh [24713.70] Heat from DHN 33626.65MWh
Heat from DHN 33626.65MWh [7536.09] Building level heatpumps 9162.78MWh
Heat from DHN 33626.65MWh [26085.94] Heat exchanger (in) 26085.94MWh
Electricity consumption 42423.69MWh [778.50] Electrical heater 762.93MWh
Electrical heater 762.93MWh [762.93] Space heating 31191.91MWh
Electricity consumption 42423.69MWh [2003.50] Building level heatpumps 9162.78MWh
Building level heatpumps 9162.78MWh [9034.37] Space heating 31191.91MWh
Building level heatpumps 9162.78MWh [128.41] Domestic hot water 906.24MWh
Heat exchanger (in) 26085.94MWh [21395.21] Space heating 31191.91MWh
Heat exchanger (in) 26085.94MWh [777.83] Domestic hot water 906.24MWh 
Local generation and storage 34350.95MWh [23429.67] Electricity consumption 42423.69MWh
Electricity consumption 42423.69MWh [5891.00] Electricity (export) 5891.00MWh
"""




fixed_color_mapping = {
    "Electricity (import) 18996.44MWh": "#1f77b4",
    "Electricity consumption 42423.69MWh": "#ff7f0e",
    "Building Integrated Photovoltaics (BIPV) 19804.06MWh": "#2ca02c",
    "Electricity (export) 5891.00MWh": "#d62728",
    "District-level heatpumps 24713.70MWh": "#9467bd",
    "District-level PV 5386.41MWh": "#8c564b",
    "Data centre 12546.32MWh": "#e377c2",
    "ORC 327.00MWh": "#bcbd22",
    "Heat exchanger (in) 26085.94MWh": "#17becf",
    "Electrical appliances 7368.81MWh": "#FF5733",
    "District-level Battery 8833.47MWh": "#33FF57",
    "Heat from DHN 33626.65MWh": "#3357FF",
    "Electrical heater 762.93MWh": "#FF33A1",
    "Space heating 31191.91MWh": "#A133FF",
    "Building level heatpumps 9162.78MWh": "#33FFA1",
    "Domestic hot water 906.24MWh": "#FF5733",
    "Local generation and storage 34350.95MWh": "#FFD700",
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
    node_x_positions = [0.1 if label in ["Electricity (import) 18996.44MWh", "Building Integrated Photovoltaics (BIPV) 19804.06MWh", "District-level PV 5386.41MWh", "Data centre 12546.32MWh", "ORC 327.00MWh", "Electrical appliances 7368.81MWh", "District-level Battery 8833.47MWh", "District-level heatpumps 24713.70MWh", "Heat from DHN 26085.94MWh", "Electrical heater 762.93MWh", "Building level heatpumps 9162.78MWh", "Heat exchanger (in) 26085.94MWh", "Local generation and storage 34350.95MWh"] else 0.9 for label in labels]

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
