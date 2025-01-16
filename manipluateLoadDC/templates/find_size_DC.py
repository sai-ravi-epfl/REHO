import pandas as pd
import pickle
import matplotlib.pyplot as plt

# Function to read the pickle file
def read_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        return data

# List of pickle file paths
'''pickle_files = [
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_50kW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_1MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_2MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_5MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_10MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_20MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_30MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_40MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_True_50MW.pickle',
]
'''
'''
pickle_files = [
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_50kW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_1MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_2MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_5MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_10MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_20MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_30MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_40MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_False_50MW.pickle',
]
'''
pickle_files = [
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_50kW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_1MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_2MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_5MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_10MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_20MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_30MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_40MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_50MW.pickle',
]

# Initialize an empty DataFrame to store the results
result_df = pd.DataFrame(columns=['size_DC', 'Q_building', 'Q_DC', 'E_HP', 'E_DC'])

# Process each pickle file
for file_path in pickle_files:
    # Read the pickle file
    data = read_pickle_file(file_path)

    # Extract the DataFrame
    df_annuals = data['gwp'][0]['df_Annuals']
    df_annuals = pd.DataFrame(df_annuals)

    # Extract the size of DC from the pickle file name or content
    size_DC = file_path.split('_')[-1].replace('.pickle', '')

    # Define the buildings list, Extract values from 'Demand_MWh' for the buildings and sum the 'Demand_MWh' values
    buildings = [f'DHN_hex_in_Building{i}' for i in range(1, 25)]
    df_heat_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                       (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_demand_mwh = df_heat_buildings['Demand_MWh'].sum()

    # Extract values from 'Supply_MWh' for the data centre
    df_heat_DC_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                   (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')]
    df_heat_DC_ORC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                    (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')]
    total_DC_supply_mwh = df_heat_DC_HP['Supply_MWh'].sum() + df_heat_DC_ORC['Demand_MWh'].sum()

    # Extract values from 'Demand_MWh' for the main heat pump
    df_heat_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
    total_HP_supply_mwh = df_heat_HP['Demand_MWh'].sum()

    # Extract values from 'Demand_MWh' for the DC
    df_elec_DC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                (df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')]
    total_DC_supply_mwh_elec = df_elec_DC['Demand_MWh'].sum()

    # Append the results to the DataFrame using pd.concat
    new_row = pd.DataFrame({
        'size_DC': [size_DC],
        'Q_building': [total_demand_mwh],
        'Q_DC': [total_DC_supply_mwh],
        'E_HP': [total_HP_supply_mwh],
        'E_DC': [total_DC_supply_mwh_elec]
    })

    result_df = pd.concat([result_df, new_row], ignore_index=True)

# Save the result to a CSV file
result_df.to_csv('result_ORC_true.csv', index=False)

### plot results
# plot size of DC on x-axis, plot electricity consumption of the heat pump and the data centre on left y-axis, plot the ratio of the heat supplied by the data centre to the heat required by the buildings on the right y-axis

# Convert size_DC to numeric values for plotting
result_df['size_DC'] = result_df['size_DC'].apply(lambda x: float(x.replace('kW', '')) / 1000 if 'kW' in x else float(x.replace('MW', '')))

# Plot the results
fig, ax1 = plt.subplots()

color_hp = 'tab:red'
color_dc = 'tab:orange'
color_ratio = 'tab:blue'

ax1.set_xlabel('Size of Data Centre (MW)')
ax1.set_ylabel('Electricity Consumption (MWh)', color=color_hp)
ax1.plot(result_df['size_DC'], result_df['E_HP'], color=color_hp, marker='o', label='Heat Pump')
ax1.plot(result_df['size_DC'], result_df['E_DC'], color=color_dc, marker='o', label='Data Centre')
ax1.tick_params(axis='y', labelcolor=color_hp)
ax1.legend(loc='upper left')
ax1.grid(True)  # Add gridlines

ax2 = ax1.twinx()
ax2.set_ylabel('Heat Ratio', color=color_ratio)
ax2.plot(result_df['size_DC'], result_df['Q_DC'] / result_df['Q_building'], color=color_ratio, marker='o', label='Heat Ratio')
ax2.tick_params(axis='y', labelcolor=color_ratio)
ax2.legend(loc='upper right')
ax2.grid(True)  # Add gridlines

#plt.title('ORC_all_the_time = False')
plt.title('BAU')
plt.show()
# Save the plot to a file with higher quality
fig.savefig('plot_BAU.png', dpi=300)