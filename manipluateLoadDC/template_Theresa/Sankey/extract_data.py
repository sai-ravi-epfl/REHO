import plotly.graph_objects as go
import re
import pandas as pd
import pickle
from pathlib import Path

# This script creates csv with data needed for creating Sankey diagrams

def read_pickle_file(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        return data

## read excel file
# Initialize an empty DataFrame to store the results
result_df = pd.DataFrame(columns=[
    'Heat_from_DHN','DHN_hex_heat', 'Q_DHW_demand', 'Q_SH_demand', 'Q_DHW_by_DHN', 'Q_SH_by_DHN', 'Q_DC_ORC_demand',
    'Q_DC_HP_supply', 'Q_main_HP_supply', 'Heat_DC_supply', 'Heat_direct_supply', 'E_building_demand',
    'E_HP_demand', 'E_DC_HP_demand', 'E_DC_demand','elec_to_DC_demand','PV_to_DC', 'E_battery_demand', 'E_battery_supply',
    'E_pv_supply', 'E_PV_district_supply', 'E_ORC_supply',
    'E_network_supply', 'E_network_demand',
    'E_electricalHeater_demand', 'Q_electricalHeater_supply_SH', 'Q_electricalHeater_supply_Heat',
    'Q_electricalHeater_supply_DHW', 'E_heatpumps_SH_demand', 'Q_heatpumps_SH_supply',
    'Q_heatpumps_Heat_demand', 'Q_heatpumps_DHW_supply',
    'E_elec_consumption_minus_export_and_DC', 'PV_generation_total',
    'PV_generation_to_elec_consumption',
    ])

## path to excel files
pickle_files = [r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\results\ORC_Heat_recovery_with_PV_district_no_shifting_grid_connected.pickle',
                r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\results\ORC_HP_Heat_recovery_with_PV_district_no_shifting_grid_connected.pickle',
                r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\results\ORC_Heat_recovery_with_PV_district_shifted_grid_connected.pickle',
                r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\results\ORC_HP_Heat_recovery_with_PV_district_shifted_grid_connected.pickle']


# Process each pickle file
for file_path in pickle_files:
    # Read the pickle file
    data = read_pickle_file(file_path)

    # Extract the DataFrame
    df_annuals = data['df_Annuals']
    df_annuals = pd.DataFrame(df_annuals)

    ### HEAT DEMANDS
    # Define the buildings list, Extract values from 'Demand_MWh' for the buildings heat and sum the 'Demand_MWh' values
    buildings = [f'DHN_hex_in_Building{i}' for i in range(1, 25)]

    # Extract values from 'Demand_MWh' for the buildings heat and sum the 'Demand_MWh' values
    df_heat_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_demand_mwh = df_heat_buildings['Demand_MWh'].sum()

    # Extract DHW demand from the buildings
    buildings = [f'Building{i}' for i in range(1, 25)]
    df_dhw_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'DHW') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_dhw_demand_mwh = df_dhw_buildings['Demand_MWh'].sum()

    # Extract the SH demand from the buildings
    buildings = [f'Building{i}' for i in range(1, 25)]
    df_sh_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'SH') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_sh_demand_mwh = df_sh_buildings['Demand_MWh'].sum()

    # SH supplied by DHN
    buildings = [f'DHN_hex_in_Building{i}' for i in range(1, 25)]
    df_SH_DHN = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'SH') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_SH_DHN_supply_mwh = df_SH_DHN['Supply_MWh'].sum() if not df_SH_DHN.empty else 0

    # DHW supplied by DHN
    buildings = [f'DHN_hex_in_Building{i}' for i in range(1, 25)]
    df_DHW_DHN = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'DHW') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_DHW_DHN_supply_mwh = df_DHW_DHN['Supply_MWh'].sum() if not df_DHW_DHN.empty else 0

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

    # heat supplied by electrical heater
    buildings = [f'ElectricalHeater_SH_Building{i}' for i in range(1, 25)]
    df_electricalHeater_Heat = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_electricalHeater_Heat_supply_mwh = df_electricalHeater_Heat['Supply_MWh'].sum() if not df_electricalHeater_Heat.empty else 0

    # heat supplied by electrical heater DHW
    buildings = [f'ElectricalHeater_DHW_Building{i}' for i in range(1, 25)]
    df_electricalHeater_DHW = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'DHW') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_electricalHeater_DHW_supply_mwh = df_electricalHeater_DHW['Supply_MWh'].sum() if not df_electricalHeater_DHW.empty else 0


    buildings = [f'ElectricalHeater_SH_Building{i}' for i in range(1, 25)]
    df_electricalHeater_SH = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'SH') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_electricalHeater_SH_supply_mwh = df_electricalHeater_SH['Supply_MWh'].sum() if not df_electricalHeater_SH.empty else 0

    # heat supplied by heat pumps in buildings
    buildings = [f'HeatPump_DHN_Building{i}' for i in range(1, 25)]
    df_heatpumps_Heat = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_HeatPump_DHN_Building_Heat_demand_mwh = df_heatpumps_Heat['Demand_MWh'].sum() if not df_heatpumps_Heat.empty else 0

    # heat supplied by heat pumps in buildings DHW
    buildings = [f'HeatPump_DHN_Building{i}' for i in range(1, 25)]
    df_heatpumps_DHW = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'DHW') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_HeatPump_DHN_Building1_DHW_supply_mwh = df_heatpumps_DHW['Supply_MWh'].sum() if not df_heatpumps_DHW.empty else 0

    buildings = [f'HeatPump_DHN_Building{i}' for i in range(1, 25)]
    df_heatpumps_SH = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'SH') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_HeatPump_DHN_Building1_SH_supply_mwh = df_heatpumps_SH['Supply_MWh'].sum() if not df_heatpumps_SH.empty else 0

    ### ELECTRICITY DEMANDS
    # electricity demand electrical heater
    buildings = [f'ElectricalHeater_SH_Building{i}' for i in range(1, 25)]
    df_electricalHeater_SH = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_electricalHeater_SH_demand_mwh = df_electricalHeater_SH['Demand_MWh'].sum() if not df_electricalHeater_SH.empty else 0

    # electricity demand heat pumps buildings
    buildings = [f'HeatPump_DHN_Building{i}' for i in range(1, 25)]
    df_heatpumps_SH = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_HeatPump_DHN_Building1_SH_demand_mwh = df_heatpumps_SH['Demand_MWh'].sum() if not df_heatpumps_SH.empty else 0


    # Extract the electricity demand from the buildings
    buildings = [f'Building{i}' for i in range(1, 25)]
    df_elec_buildings = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub').isin(buildings))]
    total_elec_demand_mwh = df_elec_buildings['Demand_MWh'].sum()

    # Extract electricity demand for the main heat pump
    df_elec_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
    total_HP_demand_mwh = df_elec_HP['Demand_MWh'].sum() if not df_heat_HP.empty else 0

    # Extract electricity demand for the HeatPump_DataCentre_district
    df_elec_DC_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                   (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')]
    total_DC_HP_demand_mwh_elec = df_elec_DC_HP['Demand_MWh'].sum() if not df_elec_DC_HP.empty else 0

    # Extract electricity demand for the DC
    df_elec_DC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                (df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')]
    total_DC_demand_mwh_elec = df_elec_DC['Demand_MWh'].sum() if not df_elec_DC.empty else 0

    # Extract electricity demand for the battery
    df_elec_battery_demand= df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') & (df_annuals.index.get_level_values('Hub') == 'Battery_district')]
    total_battery_demand_mwh_elec = df_elec_battery_demand['Demand_MWh'].sum() if not df_elec_battery_demand.empty else 0

    ### Electricity supply
    # Extract electricity supply from Battery_district
    df_elec_battery = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                     (df_annuals.index.get_level_values('Hub') == 'Battery_district')]
    total_battery_supply_mwh_elec = df_elec_battery['Supply_MWh'].sum() if not df_elec_battery.empty else 0

    # Extract electricity supply from PV_buildings
    PV_Building = [f'PV_Building{i}' for i in range(1, 25)]
    df_elec_pv = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity')
                                & (df_annuals.index.get_level_values('Hub').isin(PV_Building))]
    total_pv_supply_mwh_elec = df_elec_pv['Supply_MWh'].sum() if not df_elec_pv.empty else 0

    # Extract electricity supply from PV_buildings
    df_elec_PV_district = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                     (df_annuals.index.get_level_values('Hub') == 'PV_district')]
    total_pv_district_supply_mwh_elec = df_elec_PV_district['Supply_MWh'].sum() if not df_elec_pv.empty else 0

    # Extract electricity supply from ORC_EPFL_district
    df_elec_ORC = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                 (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')]
    total_ORC_supply_mwh_elec = df_elec_ORC['Supply_MWh'].sum() if not df_elec_ORC.empty else 0

    # Extract electricity supply from Network
    df_elec_network = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                     (df_annuals.index.get_level_values('Hub') == 'Network')]
    total_network_supply_mwh_elec = df_elec_network['Supply_MWh'].sum() if not df_elec_network.empty else 0

    # Extract electricity demand from Network
    df_elec_network_demand = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                             (df_annuals.index.get_level_values('Hub') == 'Network')]
    total_network_demand_mwh_elec = df_elec_network_demand['Demand_MWh'].sum() if not df_elec_network_demand.empty else 0

    ### Intraday storage supply
    df_TES_intraday_supply = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                     (df_annuals.index.get_level_values('Hub') == 'TES_intraday_district')]
    total_TES_intraday_supply_mwh_elec = df_TES_intraday_supply['Supply_MWh'].sum() if not df_TES_intraday_supply.empty else 0

    ### Intraday storage demand
    df_TES_intraday_demand = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                            (df_annuals.index.get_level_values('Hub') == 'TES_intraday_district')]
    total_TES_intraday_demand_mwh_elec = df_TES_intraday_demand['Demand_MWh'].sum() if not df_TES_intraday_demand.empty else 0

    # Extract data import
    df_data_import = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Data') &(df_annuals.index.get_level_values('Hub') == 'Network')]
    total_data_supply_mwh = df_data_import['Supply_MWh'].sum() if not df_data_import.empty else 0

    # Extract data inhouse
    df_data_inhouse = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Data') &(df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')]
    total_data_inhouse_mwh = df_data_inhouse['Supply_MWh'].sum() if not df_data_inhouse.empty else 0


    # total PV supply (district and buildings)
    PV_generation_total = total_pv_supply_mwh_elec + total_pv_district_supply_mwh_elec

    # total PV generation to electricity consumption
    PV_generation_to_elec_consumption = PV_generation_total - total_network_demand_mwh_elec

    ## total electricity demand
    df_total_elec_concumption = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity')]
    total_elec_consumption = df_total_elec_concumption['Demand_MWh'].sum() if not df_total_elec_concumption.empty else 0

    ## total electricity consumption (minus export)
    total_elec_consumption_minus_export = total_elec_consumption - total_network_demand_mwh_elec

    ## heat from DHN = district heatpump, datacentre heatpump and direct ehat supply
    heat_from_DHN = total_HP_supply_mwh + total_DC_HP_supply_mwh + DC_direct_heat_supply_mwh


    # Append the results to the DataFrame using pd.concat
    new_row = pd.DataFrame({
        'Heat_from_DHN': [heat_from_DHN],
        'DHN_hex_heat': [total_demand_mwh],
        'Q_DHW_demand': [total_dhw_demand_mwh],
        'Q_SH_demand': [total_sh_demand_mwh],
        'Q_DHW_by_DHN': [total_DHW_DHN_supply_mwh],
        'Q_SH_by_DHN': [total_SH_DHN_supply_mwh],
        'Q_DC_ORC_demand': [total_DC_ORC_demand_mwh],
        'Q_DC_HP_supply': [total_DC_HP_supply_mwh],
        'Q_main_HP_supply': [total_HP_supply_mwh],
        'Heat_DC_supply': [total_Heat_DataCentre_EPFL_district],
        'Heat_direct_supply': [DC_direct_heat_supply_mwh],
        'E_building_demand': [total_elec_demand_mwh],
        'E_HP_demand': [total_HP_demand_mwh],
        'E_DC_HP_demand': [total_DC_HP_demand_mwh_elec],
        'E_DC_demand': [total_DC_demand_mwh_elec],
        'E_battery_demand': [total_battery_demand_mwh_elec],
        'E_battery_supply': [total_battery_supply_mwh_elec],
        'E_pv_supply': [total_pv_supply_mwh_elec],
        'E_PV_district_supply': [total_pv_district_supply_mwh_elec],
        'E_ORC_supply': [total_ORC_supply_mwh_elec],
        'E_network_supply': [total_network_supply_mwh_elec],
        'E_network_demand': [total_network_demand_mwh_elec],
        'E_electricalHeater_demand': [total_electricalHeater_SH_demand_mwh],
        'Q_electricalHeater_supply_SH': [total_electricalHeater_SH_supply_mwh],
        'Q_electricalHeater_supply_Heat': [total_electricalHeater_Heat_supply_mwh],
        'Q_electricalHeater_supply_DHW': [total_electricalHeater_DHW_supply_mwh],
        'E_heatpumps_SH_demand': [total_HeatPump_DHN_Building1_SH_demand_mwh],
        'Q_heatpumps_SH_supply': [total_HeatPump_DHN_Building1_SH_supply_mwh],
        'Q_heatpumps_Heat_demand': [total_HeatPump_DHN_Building_Heat_demand_mwh],
        'Q_heatpumps_DHW_supply': [total_HeatPump_DHN_Building1_DHW_supply_mwh],
        'E_elec_consumption_minus_export': [total_elec_consumption_minus_export],
        'PV_generation_total': [PV_generation_total],
        'PV_generation_to_elec_consumption': [PV_generation_to_elec_consumption],
    })

    result_df = pd.concat([result_df, new_row], ignore_index=True)

# Save the result to a CSV file
result_df.to_csv('results_scenarios_new.csv', index=False)
