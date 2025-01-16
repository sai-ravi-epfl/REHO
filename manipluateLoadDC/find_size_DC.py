import pandas as pd
import pickle
import matplotlib.pyplot as plt

# Function to read the pickle file
def read_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        return data

# List of pickle file paths

pickle_files = [
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_50kW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_1MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_2MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_5MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_10MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_20MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_30MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_40MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_50MW.pickle',
]

'''
pickle_files = [
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_50kW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_1MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_2MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_5MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_10MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_20MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_30MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_40MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_50MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_50MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_60MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_70MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_80MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_90MW.pickle',
    r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_ORC_HP_100MW.pickle',
]

'''
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
'''
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

### HEAT
    # Define the buildings list, Extract values from 'Demand_MWh' for the buildings and sum the 'Demand_MWh' values
    buildings = [f'DHN_hex_in_Building{i}' for i in range(1, 25)]
    df_heat_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                       (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_demand_mwh = df_heat_buildings['Demand_MWh'].sum() if not df_heat_buildings.empty else 0

    # Heat supplied Data centre
    df_heat_DC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                (df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')]
    total_Heat_DataCentre_EPFL_district =df_heat_DC['Supply_MWh'].sum() if not df_heat_DC.empty else 0

    # heat demand ORC
    df_heat_DC_ORC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                    (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')]
    total_DC_ORC_demand_mwh = df_heat_DC_ORC['Demand_MWh'].sum() if not df_heat_DC_ORC.empty else 0

    # heat directly supplied
    DC_direct_heat_supply_mwh = total_Heat_DataCentre_EPFL_district - total_DC_ORC_demand_mwh

    # Heat supplied of data centre heatpump of the data centre
    df_heat_supply_DC_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                   (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')]
    total_DC_HP_supply_mwh = df_heat_supply_DC_HP['Supply_MWh'].sum() if not df_heat_supply_DC_HP.empty else 0

### Electricity
    # Electricity demand of the the main heat pump
    df_elec_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
    total_HP_demand_mwh = df_elec_HP['Demand_MWh'].sum() if not df_elec_HP.empty else 0

    # Electricity demand for the HeatPump_DataCentre_district
    df_elec_DC_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                   (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')]
    total_DC_HP_demand_mwh_elec = df_elec_DC_HP['Demand_MWh'].sum() if not df_elec_DC_HP.empty else 0

    # Electricity demand of DC
    df_elec_DC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                (df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')]
    total_DC_supply_mwh_elec = df_elec_DC['Demand_MWh'].sum() if not df_elec_DC.empty else 0

    # electricity supply of ORC
    df_elec_ORC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')]
    total_DC_ORC_supply_mwh = df_elec_ORC['Supply_MWh'].sum() if not df_elec_ORC.empty else 0

### Q_DC

    # Heat supply of the the main heat pump
    df_heat_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
    total_HP_supply_mwh = df_heat_HP['Supply_MWh'].sum()

    # Calculate COP geothermal and handle zero division error
    try:
        if total_HP_demand_mwh == 0:
            raise ZeroDivisionError("total_HP_demand_mwh is zero, cannot divide by zero.")
        COP_geothermal_current = total_HP_supply_mwh / total_HP_demand_mwh
        if COP_geothermal_current != 0:
            COP_geothermal = COP_geothermal_current
        elif COP_geothermal is None:
            raise ValueError("Initial COP value is None and current COP is zero.")
        else:
            COP_geothermal_current = COP_geothermal
    except ZeroDivisionError as e:
        print(f"Warning: {e}")
        if COP_geothermal is None:
            raise ValueError("Initial COP value is None and division by zero occurred.")
        else:
            COP_geothermal_current = COP_geothermal

    print(
        f"total_HP_supply_mwh: {total_HP_supply_mwh}, total_HP_demand_mwh: {total_HP_demand_mwh}, COP_geothermal_current: {COP_geothermal_current}")

    total_DC = 0.7 * total_DC_ORC_supply_mwh * COP_geothermal_current + DC_direct_heat_supply_mwh + total_DC_HP_supply_mwh - total_DC_HP_demand_mwh_elec
    # Append the results to the DataFrame using pd.concat
    new_row = pd.DataFrame({
        'size_DC': [size_DC],
        'Q_building': [total_demand_mwh],
        'Q_DC': [total_DC],
        'E_HP': [total_HP_demand_mwh],
        'E_DC': [total_DC_supply_mwh_elec],
        'E_HP_DC':[total_DC_HP_demand_mwh_elec]
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
color_ac = 'tab:purple'
color_ratio = 'tab:blue'

ax1.set_xlabel('Size of Data Centre (MW)')
ax1.set_ylabel('Electricity Consumption (MWh)', color=color_hp)
ax1.plot(result_df['size_DC'], result_df['E_HP'], color=color_hp, marker='o', label='Main Heat Pump')
ax1.plot(result_df['size_DC'], result_df['E_DC'], color=color_dc, marker='o', label='Data Centre')
#ax1.plot(result_df['size_DC'], result_df['E_HP_DC'], color=color_ac, marker='o', label='Heat Pump Data Centre')
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
plt.title('ORC')
plt.show()
# Save the plot to a file with higher quality
fig.savefig('plot_ORC.png', dpi=3000)