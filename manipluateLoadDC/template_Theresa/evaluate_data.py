import pickle
import pandas as pd

def read_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        return data

# List of pickle file paths
pickle_files = [
    r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_BAU_168h_2MW.pickle',
    r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_ORC_168h_2MW_DC.pickle',
    r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_ORC_HP_168h_2MW_DC.pickle',
]

# Initialize an empty DataFrame to store the results
result_df = pd.DataFrame(columns=[
    'size_DC', 'Q_building', 'Q_DHW', 'Q_SH', 'Q_DC_ORC', 'Q_DC_HP_demand','Q_DC_HP_supply','Q_main_HP', 'Heat_DC_supply', 'Heat_direct_supply', 'E_building',
    'E_HP', 'E_DC_HP', 'E_DC', 'E_battery_demand', 'E_battery_supply', 'E_pv_supply', 'E_ORC_supply',
    'E_network_supply', 'Solar_gains'
])

# Process each pickle file
for file_path in pickle_files:
    # Read the pickle file
    data = read_pickle_file(file_path)

    # Extract the DataFrame
    df_annuals = data['gwp'][0]['df_Annuals']
    df_annuals = pd.DataFrame(df_annuals)

    # Extract the size of DC from the pickle file name or content
    size_DC = file_path.split('_')[-1].replace('.pickle', '')

    ### HEAT DEMANDS
    # Define the buildings list, Extract values from 'Demand_MWh' for the buildings heat and sum the 'Demand_MWh' values
    buildings = [f'DHN_hex_in_Building{i}' for i in range(1, 25)]
    df_heat_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                       (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_demand_mwh = df_heat_buildings['Demand_MWh'].sum()

    # Extract DHW demand from the buildings
    buildings = [f'Building{i}' for i in range(1, 25)]
    df_dhw_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'DHW') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_dhw_demand_mwh = df_dhw_buildings['Demand_MWh'].sum()

    # Extract the SH demand from the buildings
    df_sh_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'SH') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_sh_demand_mwh = df_sh_buildings['Demand_MWh'].sum()

    # heat demand for the ORC
    df_heat_DC_ORC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                    (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')]
    total_DC_ORC_demand_mwh = df_heat_DC_ORC['Demand_MWh'].sum() if not df_heat_DC_ORC.empty else 0

    # heat demand for the heatpump of the data centre
    df_heat_demand_DC_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                   (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')]
    total_DC_HP_demand_mwh = df_heat_demand_DC_HP['Demand_MWh'].sum() if not df_heat_demand_DC_HP.empty else 0

    ### HEAT SUPPLIES
    # Extract values from 'Supply_MWh' for the heatpump of the data centre
    df_heat_supply_DC_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                   (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')]
    total_DC_HP_supply_mwh = df_heat_supply_DC_HP['Supply_MWh'].sum() if not df_heat_supply_DC_HP.empty else 0

    # Extract values from 'Supply_MWh' for the geothermal heat pump
    df_heat_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') & (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
    total_HP_supply_mwh = df_heat_HP['Supply_MWh'].sum() if not df_heat_HP.empty else 0

    # Heat supplied Data centre
    df_heat_DC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                (df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')]
    total_Heat_DataCentre_EPFL_district =df_heat_DC['Supply_MWh'].sum()

    # heat directly supplied
    DC_direct_heat_supply_mwh = total_Heat_DataCentre_EPFL_district - total_DC_ORC_demand_mwh

    ### ELECTRICITY DEMANDS
    # Extract the electricity demand from the buildings
    df_elec_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_elec_demand_mwh = df_elec_buildings['Demand_MWh'].sum()

    # Extract electricity demand for the main heat pump
    df_elec_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
    total_HP_demand_mwh = df_elec_HP['Demand_MWh'].sum() if not df_heat_HP.empty else 0

    # Extract electricity demand for the HeatPump_DataCentre_district
    df_elec_DC_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                   (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')]
    total_DC_HP_supply_mwh_elec = df_elec_DC_HP['Demand_MWh'].sum() if not df_elec_DC_HP.empty else 0

    # Extract electricity demand for the DC
    df_elec_DC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                (df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')]
    total_DC_supply_mwh_elec = df_elec_DC['Demand_MWh'].sum() if not df_elec_DC.empty else 0

    # Extract electricity demand for the battery
    df_elec_battery_demand= df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub') == 'Battery_district')]
    total_battery_demand_mwh_elec = df_elec_battery_demand['Demand_MWh'].sum() if not df_elec_battery_demand.empty else 0

    ### Electricity supply
    # Extract electricity supply from Battery_district
    df_elec_battery = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                     (df_annuals.index.get_level_values('Hub') == 'Battery_district')]
    total_battery_supply_mwh_elec = df_elec_battery['Supply_MWh'].sum() if not df_elec_battery.empty else 0

    # Extract electricity supply from PV_district
    PV_Building = [f'PV_Building{i}' for i in range(1, 25)]
    df_elec_pv = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity')
                                & (df_annuals.index.get_level_values('Hub').isin(PV_Building))]
    total_pv_supply_mwh_elec = df_elec_pv['Supply_MWh'].sum() if not df_elec_pv.empty else 0

    # Extract electricity supply from ORC_EPFL_district
    df_elec_ORC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                 (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')]
    total_ORC_supply_mwh_elec = df_elec_ORC['Supply_MWh'].sum() if not df_elec_ORC.empty else 0

    # Extract electricity supply from Network
    df_elec_network = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                     (df_annuals.index.get_level_values('Hub') == 'Network')]
    total_network_supply_mwh_elec = df_elec_network['Supply_MWh'].sum() if not df_elec_network.empty else 0

    ### Solar gains
    # Extract the solar gains from the buildings
    df_solar_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'SolarGains') &
                                        (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_solar_gains_mwh = df_solar_buildings['Demand_MWh'].sum()

    ### GWP

    ### TOTEX


    # Append the results to the DataFrame using pd.concat
    new_row = pd.DataFrame({
        'size_DC': [size_DC],
        'Q_building': [total_demand_mwh],
        'Q_DHW': [total_dhw_demand_mwh],
        'Q_SH': [total_sh_demand_mwh],
        'Q_DC_ORC': [total_DC_ORC_demand_mwh],
        'Q_DC_HP_demand': [total_DC_HP_demand_mwh],
        'Q_DC_HP_supply': [total_DC_HP_supply_mwh],
        'Q_main_HP': [total_HP_supply_mwh],
        'Heat_DC_supply': [total_Heat_DataCentre_EPFL_district],
        'Heat_direct_supply': [DC_direct_heat_supply_mwh],
        'E_building': [total_elec_demand_mwh],
        'E_HP': [total_HP_demand_mwh],
        'E_DC_HP': [total_DC_HP_supply_mwh_elec],
        'E_DC': [total_DC_supply_mwh_elec],
        'E_battery_demand': [total_battery_demand_mwh_elec],
        'E_battery_supply': [total_battery_supply_mwh_elec],
        'E_pv_supply': [total_pv_supply_mwh_elec],
        'E_ORC_supply': [total_ORC_supply_mwh_elec],
        'E_network_supply': [total_network_supply_mwh_elec],
        'Solar_gains': [total_solar_gains_mwh]
    })

    result_df = pd.concat([result_df, new_row], ignore_index=True)

# Save the result to a CSV file
result_df.to_csv('results_scenarios_new.csv', index=False)



