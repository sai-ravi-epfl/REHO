import pandas as pd
import plotly.graph_objects as go
import os
from sklearn.preprocessing import MinMaxScaler
from reho.model.reho import *
from reho.paths import *

### File Paths
excel_file_path = path_to_results + '/ALL_EPFL_BAU_14_TD_gwp.xlsx' #replace by excel file path with typical days from REHO
dat_file_path = path_to_clustering + '/index_Pully_14_24_T_I_E_D_CS.dat' #index dat file from clustering
output_csv_path = 'reconstructed_year_14clusters.csv' # path and name of where you want to store your yearly profile as a csv
number_periods = 14 + 1

### 1. Read and Process Excel File
# Read the Excel file into a DataFrame
df = pd.read_excel(excel_file_path, sheet_name='df_Unit_t') # change the sheet which you want make an yearly profile out of
# Forward-fill missing values in 'Layer' and 'Period' (if they are omitted in subsequent rows)
df['Layer'] = df['Layer'].ffill()
df['Unit'] = df['Unit'].ffill()
df['Period'] = df['Period'].ffill()

# Debug: Print column names and unique values in 'Layer' and 'Unit'
print("Columns in DataFrame:", df.columns)
print("Unique values in 'Layer':", df['Layer'].unique())
print("Unique values in 'Unit':", df['Unit'].unique())

### 2. Read and Process the .dat File for index
data = []
with open(dat_file_path, "r") as f:
    lines = f.readlines()

# Debug: Print the raw file lines
print("Raw file lines:")
for line in lines:
    print(repr(line))

# Process each line after the header.
# Expected format per line: <param> <PeriodOfYear> <TimeOfYear>
for line in lines[1:]:
    # Remove leading/trailing whitespace and split on any whitespace
    parts = line.strip().split()

    # Ensure there are at least three parts per line
    if len(parts) >= 3:
        try:
            param_val = int(parts[0])
            period_val = int(parts[1])
            time_val = int(parts[2])
        except ValueError:
            print("Skipping line with conversion error:", line)
            continue

        data.append({
            "TimeInYear": param_val,
            "PeriodOfYear": period_val,
            "TimeOfYear": time_val
        })
    else:
        print("Skipping a line that doesn't match the expected format:", line)

# Create a DataFrame from the parsed data
index_df = pd.DataFrame(data)
print("Index DataFrame:")
print(index_df.head())

### 2.1 Get the rows where PV_Building1 to PV_Building24 are present
# Filter the rows where 'Layer' is 'Electricity' and 'Unit' is 'PV_BuildingX' where X are from 1 to 24
df_filtered = df[(df['Layer'].str.lower() == 'electricity') & df['Unit'].str.match(r'PV_Building\d+', case=False)]
print("Filtered DataFrame:")
print(df_filtered.head())

### 2.2 Add rows at right position so that for every period 24 hours are given and add a value of 0 in those rows
# Create a new DataFrame with all possible combinations of 'Period' and 'Time' (1 to 24)
all_periods = list(range(1, number_periods))
all_times = list(range(1, 25))
all_combinations = [(period, time) for period in all_periods for time in all_times]
all_combinations_df = pd.DataFrame(all_combinations, columns=['Period', 'Time'])

### 3. Group the Building Data by Period and Time
# Sum 'Units_supply' of 'PV_Building1' up to 'PV_Building24' for each 'Period' and 'Time'
grouped_result = df_filtered.groupby(['Period', 'Time'])['Units_supply'].sum().reset_index()
print("Grouped Result DataFrame:")
print(grouped_result.head())

### 4. Merge the Index DataFrame with the Grouped Building Data
# Merge on 'PeriodOfYear' and 'TimeOfYear' from index_df and 'Period' and 'Time' from grouped_result
merged_df = pd.merge(index_df, grouped_result,
                     left_on=['PeriodOfYear', 'TimeOfYear'],
                     right_on=['Period', 'Time'],
                     how='left')
print("Merged DataFrame:")
print(merged_df.head())

### 5. Reconstruct the Final DataFrame
# Select the desired columns and set 'TimeInYear' as the index
reconstructed_df = merged_df[['TimeInYear', 'Units_supply']].copy()
reconstructed_df.set_index('TimeInYear', inplace=True)
print("Reconstructed DataFrame:")
print(reconstructed_df.head())

### 6. Save the Final DataFrame to a CSV File
reconstructed_df.to_csv(output_csv_path)
print("Reconstructed DataFrame saved to:", output_csv_path)

'''
### 7. Compute 5-Day Moving Averages (assuming hourly data, 5 days = 120 hours)
window_hours = 5 * 24  # 5 days = 120 hours

# Compute the moving averages and add as new columns
reconstructed_df['House_Q_heating_MA'] = reconstructed_df['House_Q_heating'].rolling(window=window_hours, min_periods=1).mean()
reconstructed_df['House_Q_DHW_MA'] = reconstructed_df['House_Q_DHW'].rolling(window=window_hours, min_periods=1).mean()

### 7. reading Datacentre profile for 50kW, normalising and changing size for 2 MW, and taking MA
path_dir = os.getcwd()
df_data = pd.read_csv( path_dir + '/data/yearly_data_centre_profile_repeated.csv')
scaler = MinMaxScaler()
df_data['Load_Profile'] = scaler.fit_transform(df_data[['Load_Profile']])
size_data_centre  = 200 #kW
df_data['Load_Profile'] = df_data['Load_Profile']*size_data_centre
window_hours_data = 30 * 24
reconstructed_df['Data_Profile_MA'] = df_data['Load_Profile'].rolling(window=window_hours_data, min_periods=1).mean()

### 8. Create an Interactive Plotly Graph
# Create a new figure
fig = go.Figure()
'''
'''
Add the moving average trace for SH Profile
fig.add_trace(go.Scatter(
    x=reconstructed_df.index,
    y=reconstructed_df['House_Q_heating_MA'],
    mode='lines',
    name='Data Profile(5-day MA)',
    line=dict(color='royalblue', width=2)
))
'''
'''
# Add the moving average trace for Data Profile
fig.add_trace(go.Scatter(
    x=reconstructed_df.index,
    y=reconstructed_df['Data_Profile_MA'],
    mode='lines',
    name='Data Profile(5-day MA)',
    line=dict(color='crimson', width=2)
))

# Add the moving average trace for Domestic Hot Water
fig.add_trace(go.Scatter(
    x=reconstructed_df.index,
    y=reconstructed_df['House_Q_DHW_MA'],
    mode='lines',
    name='Domestic Hot Water (5-day MA)',
    line=dict(color='firebrick', width=2)
))

# Refine layout for a clean, publication-quality look
fig.update_layout(
    template_Sai='plotly_white',
    title={
        'text': "5-Day Moving Average of Heat Demand Profiles",
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis=dict(
        title="Time in Year",
        showgrid=True,
        gridcolor='lightgrey'
    ),
    yaxis=dict(
        title="Heat Demand (kWh)",
        showgrid=True,
        gridcolor='lightgrey'
    ),
    legend=dict(
        title="Profile",
        x=0.09,
        y=1.05,
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='LightGray',
        borderwidth=1
    ),
    font=dict(
        family="Arial, sans-serif",
        size=12,
        color="black"
    )
)

# Show the interactive plot
fig.show()

# Optionally, save the interactive plot as an HTML file
fig.write_html("heat_demand_profile_interactive.html")
print("Interactive plot saved to 'heat_demand_profile_interactive.html'")
'''