
import pickle
import pandas as pd
import numpy as np
from pandas import ExcelWriter

def print_important_params(path, scenario, print_excel=False, save_pickle=False, pareto_id_to_save=None):
    with open(path, 'rb') as f:
        data = pickle.load(f)

    print('\n')
    print(scenario)
    print('\n')
    a = []
    b = []
    c = []
    d = []
    #for i in range(1, len(data['gwp'].keys()) + 1):
    for i in range(1, len(data['gwp'].keys())+1):
        print("Pareto ID:", i)
        print('\n')
        PV_cap = data['gwp'][i]['df_Unit'][data['gwp'][i]['df_Unit'].index.str.contains('PV_district')]['Units_Mult'].sum()
        Batery_dis_cap = data['gwp'][i]['df_Unit'].xs('Battery_district').Units_Mult
        Data_cap = data['gwp'][i]['df_Unit'].xs('DataCentre_EPFL_district').Units_Mult
        network_import = data['gwp'][i]['df_Annuals'].xs('Electricity').xs('Network')['Supply_MWh']
        network_export = data['gwp'][i]['df_Annuals'].xs('Electricity').xs('Network')['Demand_MWh']
        data_import = data['gwp'][i]['df_Annuals'].xs('Data').xs('Network')['Supply_MWh']
        battery_in = data['gwp'][i]['df_Annuals'].xs('Electricity').xs('Battery_district')['Supply_MWh']
        data_in_house = data['gwp'][i]['df_Annuals'].xs('Data').xs('DataCentre_EPFL_district')['Supply_MWh']
        data_price = data['gwp'][i]['df_Grid_t'].xs('Data').xs('Network').xs(1).xs(1)['Cost_supply']
        if 'HeatPump_DataCentre_district' in data['gwp'][i]['df_Annuals'].xs('Heat').index:
            heat_from_HPDC = data['gwp'][i]['df_Annuals'].xs('Heat').xs('HeatPump_DataCentre_district')['Supply_MWh']
        else:
            heat_from_HPDC = 0
        #orc_heat_demand = data['gwp'][i]['df_Annuals'].xs('Heat').xs('ORC_EPFL_district')['Demand_MWh']
        heat_from_HPGT = data['gwp'][i]['df_Annuals'].xs('Heat').xs('HeatPump_Geothermal_district')['Supply_MWh']
        data_GWP = data['gwp'][i]['df_Grid_t'].xs('Data').xs('Network').xs(1).xs(1)['GWP_supply']

        a.append(data_import)
        b.append(data_price)
        c.append(Data_cap)
        d.append(network_import)
        print("PV capacity:", PV_cap)
        print("Battery district capacity:", Batery_dis_cap)
        print("Battery district charge in:", battery_in)
        print("Network Import:", network_import)
        print("Network export:", network_export)
        print("Heat from DC Heatpump:", heat_from_HPDC)
        #print("ORC heat demand :", orc_heat_demand)
        print("data in house :", data_in_house)
        print("Heat from DC Geothermal:", heat_from_HPGT)
        print("Data - cloud processed:", data_import)
        print("Data centre size:", Data_cap)
        print('\n')


        # save the printed data for every pareto id in a csv (one row is one pareto id and the different columns are the printed data)

        # Save the specific Pareto ID as a pickle file
    if save_pickle:
        save_as_pickle(data['gwp'][5], r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\results\BAU.pickle')

    if print_excel:
        df = read_pickle(ORC_all_the_time)
        write_excel(df['gwp'][9], r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\BAU_9.xlsx')

    return a, b, c, d

def read_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

def write_excel(data_qjv, output_excel_path):
    with pd.ExcelWriter(output_excel_path, engine='xlsxwriter') as writer:
        for key, df in data_qjv.items():
            if isinstance(df, dict):
                for sub_key, sub_df in df.items():
                    if isinstance(sub_df, pd.DataFrame):
                        sheet_name = f"{key}_{sub_key}"[:31]
                        sub_df.to_excel(writer, sheet_name=sheet_name)
            elif isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=str(key)[:31])
    print(f"DataFrames written to {output_excel_path}")

def save_as_pickle(data, output_pickle_path):
    with open(output_pickle_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data saved as pickle file: {output_pickle_path}")

ORC_all_the_time = r"C:\Users\there\Desktop\REHO2\scripts\template_Sai\results\EPFL_BAU_Pareto_CI.pickle"
outsource, cost, data_cap, export = print_important_params(ORC_all_the_time, 'ORC all the time', print_excel=True, save_pickle=False, pareto_id_to_save=4)

check = pd.DataFrame({'Data Bought outside': outsource, 'cost': cost, 'size of DC': data_cap, 'Electricity export': export})
print(check)


