import plotly.graph_objects as go
import re

# This script creates a Sankey diagram to visualize energy flows.
# Input: Human-readable flow data in a string format.
# Output: An interactive Sankey diagram displayed using Plotly.

# Define flows in a human-readable format
flow_data = """
Electricity import 33347.58MWh [33347.58] Electricity consumption 35691.27MWh
PV panel 1949.93MWh [1949.93] Electricity consumption 35691.27MWh
Electricity consumption 35691.27MWh [25069.21] Main EPFL heat pump 43847.35MWh
Electricity consumption 35691.27MWh [4771.22] Data centre 4771.22MWh
Data centre 4771.22MWh [4580.37] Heat data centre 4580.37MWh 
Heat data centre 4580.37MWh [4580.37] ORC 4580.37MWh 
Electricity consumption 35691.27MWh [2986.91] Heat pump data centre 6733.51MWh
Heat pump data centre 6733.51MWh [6733.51] Heat from DHN 50574.59MWh
ORC 4580.37MWh [412.23] Electricity consumption 35691.27MWh
ORC 4580.37MWh [4168.14] Heat pump data centre 6733.51MWh
Electricity consumption 35691.27MWh [2834.36] Electrical appliances 2834.36MWh
Electricity consumption 35691.27MWh [29.57] Battery 29.57MWh 
Battery 29.57MWh [23.93] Electricity consumption 35691.27MWh
Main EPFL heat pump 43847.35MWh [43847.35] Heat from DHN 50574.59MWh
Heat from DHN 50574.59MWh [50574.59] Heat exchanger (in) 50574.59MWh
Heat exchanger (in) 50574.59MWh [42522.17] Space heating 42522.17MWh
Heat exchanger (in) 50574.59MWh [466.23] Domestic hot water 466.23MWh 
"""
# needed to be added:
# PV_district 1949.93MWh [1949.93] Electricity consumption 35691.27MWh
# TES_intrady_district 0.0MWh [0.0] Heat exchanger (in) 50574.59MWh


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

# Node colors (aesthetic academic palette)
node_colors = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#bcbd22", "#17becf"
]
node_colors = node_colors[:len(labels)]  # Adjust palette to the number of nodes

# Sankey diagram creation
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

# Show the figure
fig.show()