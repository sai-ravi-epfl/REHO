import pandas as pd
import csv
from datetime import datetime
import amplpy
import matplotlib.pyplot as plt

def process_and_optimize_data_GWP(path_to_load_profile_dat, path_to_emissions, path_timestamp_dat, model_path, output_single_column_dat_path):
    def read_and_process_dat(path_to_load_profile_dat, path_to_emissions):
        # Load profile of data centre after clustering
        load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')

        # Load GWP100a profile from electricity_matrix_2019_reduced.csv
        emissions_matrix = pd.read_csv(path_to_emissions, index_col=[0, 1, 2])
        gwp_row = emissions_matrix.loc[(emissions_matrix.index.get_level_values(2) == 'GWP100a') & (emissions_matrix.index.get_level_values(0) == 'CH')]
        gwp_profile = gwp_row.T
        gwp_profile.index = range(1, len(gwp_profile) + 1)
        gwp_profile.index.name = 'Hour'
        gwp_profile.columns = ['gwp']
        return load_profile, gwp_profile

    def calculate_hour_of_year(timestamp):
        dt = datetime.strptime(timestamp, '%m/%d/%Y/%H')
        new_year_day = datetime(dt.year, 1, 1)
        hour_of_year = int((dt - new_year_day).total_seconds() // 3600)
        return hour_of_year

    def convert_timestamp_to_df(path_timestamp_dat):
        data = []
        with open(path_timestamp_dat, 'r') as dat_file:
            reader = csv.reader(dat_file, delimiter='\t')
            header = next(reader)
            header.append('HourOfYear')
            for row in reader:
                timestamp = row[0]
                hour_of_year = calculate_hour_of_year(timestamp)
                row.append(hour_of_year)
                if len(row) == len(header) - 1:
                    row.insert(-1, '')
                data.append(row)
        return pd.DataFrame(data, columns=header)

    def filter_gwp_profile(timestamp_df, gwp_profile):
        days = timestamp_df['Day'].astype(int).tolist()
        extreme_hours = timestamp_df['HourOfYear'].astype(int).tolist()
        filtered_values = []
        extreme_values = []

        for hour, gwp in gwp_profile.itertuples():
            day_of_year = (hour - 1) // 24 + 1
            if day_of_year in days[:-2]:
                filtered_values.append((day_of_year, gwp))
            if hour in extreme_hours[-2:]:
                extreme_values.append(gwp)

        filtered_gwp_profile = pd.DataFrame(filtered_values, columns=['Day', 'gwp'])
        return filtered_gwp_profile, extreme_values

    def optimize_load_profile(load_profile, filtered_gwp_profile, model_path):
        T = len(load_profile) - 2
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.read(model_path)
        ampl.eval(f'let T := {T};')

        load_data = {i + 1: load for i, load in enumerate(load_profile[0][:T])}
        gwp_data = {i + 1: gwp for i, gwp in enumerate(filtered_gwp_profile['gwp'][:T])}

        # Set data in AMPL
        ampl.param['load'] = load_data
        ampl.param['objective'] = gwp_data

        ampl.solve()

        shifted_load = ampl.getVariable('shifted_load').getValues().toPandas()
        shifted_load.index.name = 'Hour'
        shifted_load.columns = ['Load_Profile']
        shifted_load.reset_index(inplace=True)

        total_gwp = ampl.getObjective('gwp').value()
        return total_gwp, shifted_load

    def save_single_column_dat(data, output_path):
        with open(output_path, 'w') as dat_file:
            for value in data:
                dat_file.write(f"{value}\n")

    load_profile, gwp_profile = read_and_process_dat(path_to_load_profile_dat, path_to_emissions)
    timestamp_df = convert_timestamp_to_df(path_timestamp_dat)
    filtered_gwp_profile, extreme_values = filter_gwp_profile(timestamp_df, gwp_profile)
    total_gwp, shifted_load_df_GWP = optimize_load_profile(load_profile, filtered_gwp_profile, model_path)

    all_values_gwp = shifted_load_df_GWP['Load_Profile'].tolist() + extreme_values
    save_single_column_dat(all_values_gwp, output_single_column_dat_path)

    return total_gwp, shifted_load_df_GWP, gwp_profile, all_values_gwp


def process_and_optimize_data_space_heating(path_to_load_profile_dat, path_to_excel_file_BAU, model_path_SH, output_single_column_dat_path):
    def extract_data(excel_file):
        # Definierte Parameter innerhalb der Funktion
        sheet_name = 'df_Buildings_t'
        column_name = 'House_Q_heating'

        # Load the Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=[column_name])

        # Extract the data from the column
        heating_data = df[column_name].tolist()

        return heating_data

    def read_and_process_csv(path_to_load_profile_dat):
        # Load profile of data centre after clustering
        load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')

        return load_profile

    def optimize_load_profile(load_profile, SH_profile, model_path):
        T = len(load_profile) - 2
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.read(model_path)
        ampl.eval(f'let T := {T};')

        load_data = {i + 1: load for i, load in enumerate(load_profile[0][:T])}
        SH_data = {i + 1: sh for i, sh in enumerate(SH_profile[:T])}

        # Set data in AMPL
        ampl.param['load'] = load_data
        ampl.param['objective'] = SH_data

        ampl.solve()

        shifted_load = ampl.getVariable('shifted_load').getValues().toPandas()
        shifted_load.index.name = 'Hour'
        shifted_load.columns = ['Load_Profile']
        shifted_load.reset_index(inplace=True)

        total_SH = ampl.getObjective('use').value()
        return total_SH, shifted_load

    def save_single_column_dat(data, output_path):
        with open(output_path, 'w') as dat_file:
            for value in data:
                dat_file.write(f"{value}\n")

    # Main execution
    heating_data = extract_data(path_to_excel_file_BAU)
    load_profile = read_and_process_csv(path_to_load_profile_dat)

    # Optimize load profile excluding the last two hours (extreme values)
    total_SH, shifted_load_df_SH = optimize_load_profile(load_profile, heating_data, model_path_SH)

    # Combine all values in a single column
    extreme_values = heating_data[-2:]
    all_values_SH = shifted_load_df_SH['Load_Profile'].tolist() + extreme_values

    # Save all values in a single column to the specified path
    save_single_column_dat(all_values_SH, output_single_column_dat_path)

    return total_SH, shifted_load_df_SH, heating_data, all_values_SH


def process_and_optimize_data_electricity_demand(path_to_load_profile_dat, path_to_excel_file_BAU, model_path_electricity, output_single_column_dat_path):
    def extract_data(excel_file):
        # Define parameters within the function
        sheet_name = 'df_Buildings_t'
        column_name = 'Domestic_electricity'

        # Load the Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=[column_name])

        # Extract the data from the column
        electricity_data = df[column_name].tolist()

        return electricity_data

    def read_and_process_csv(path_to_load_profile_dat):
        # Load profile of data centre after clustering
        load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')

        return load_profile

    def optimize_load_profile(load_profile, electricity_profile, model_path):
        T = len(load_profile) - 2
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.read(model_path)
        ampl.eval(f'let T := {T};')

        load_data = {i + 1: load for i, load in enumerate(load_profile[0][:T])}
        electricity_data = {i + 1: elec for i, elec in enumerate(electricity_profile[:T])}

        # Set data in AMPL
        ampl.param['load'] = load_data
        ampl.param['objective'] = electricity_data

        ampl.solve()

        shifted_load = ampl.getVariable('shifted_load').getValues().toPandas()
        shifted_load.index.name = 'Hour'
        shifted_load.columns = ['Load_Profile']
        shifted_load.reset_index(inplace=True)

        total_electricity_demand = ampl.getObjective('use').value()
        return total_electricity_demand, shifted_load

    def save_single_column_dat(data, output_path):
        with open(output_path, 'w') as dat_file:
            for value in data:
                dat_file.write(f"{value}\n")

    # Main execution
    electricity_data = extract_data(path_to_excel_file_BAU)
    load_profile = read_and_process_csv(path_to_load_profile_dat)

    # Optimize load profile excluding the last two hours (extreme values)
    total_electricity_demand, shifted_load_df_electricity = optimize_load_profile(load_profile, electricity_data, model_path_electricity)

    # Combine all values in a single column
    extreme_values = electricity_data[-2:]
    all_values_electricity_demand = shifted_load_df_electricity['Load_Profile'].tolist() + extreme_values

    # Save all values in a single column to the specified path
    save_single_column_dat(all_values_electricity_demand, output_single_column_dat_path)

    return total_electricity_demand, shifted_load_df_electricity, electricity_data, all_values_electricity_demand


# example for calling function of GWP
path_to_load_profile_dat = r'/scripts/templates/data/clustering/D_Pully_10_24_T_I_E_D.dat'
load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')
path_to_emissions = r'/reho/data/emissions/electricity_matrix_2019_reduced.csv'
path_timestamp_dat = r'/scripts/template/data/clustering/timestamp_Pully_10_24_T_I_E_D.dat'
model_path_gwp = r'/scripts/templates/switchLoad/afterClustering/data_heat_switch_after_clustering_gwp.mod'
output_single_column_dat_path_GWP = r'/scripts/templates/switchLoad/D_Pully_10_24_T_I_E_D.dat'

total_gwp, shifted_load_df_GWP,gwp_profile, all_values_gwp = process_and_optimize_data_GWP(path_to_load_profile_dat, path_to_emissions, path_timestamp_dat, model_path_gwp, output_single_column_dat_path_GWP)

# example for calling function of SH
path_to_load_profile_dat = r'/scripts/templates/data/clustering/D_Pully_10_24_T_I_E_D.dat'
path_to_excel_file_BAU = r'/scripts/template/results/ALL_EPFL_BAU_gwp.xlsx'
model_path_SH = r'/scripts/templates/switchLoad/afterClustering/data_heat_switch_after_clustering_use.mod'
output_single_column_dat_path_SH = r'/scripts/templates/switchLoad/D_Pully_10_24_T_I_E_D.dat'

total_SH, shifted_load_df_SH, heating_data, all_values_SH = process_and_optimize_data_space_heating(path_to_load_profile_dat, path_to_excel_file_BAU, model_path_SH, output_single_column_dat_path_SH)

# example for calling function of Electricity demand
path_to_load_profile_dat = r'/scripts/templates/data/clustering/D_Pully_10_24_T_I_E_D.dat'
path_to_excel_file_BAU = r'/scripts/template/results/ALL_EPFL_BAU_gwp.xlsx'
model_path_electricity_demand = r'/scripts/templates/switchLoad/afterClustering/data_heat_switch_after_clustering_use.mod'
output_single_column_dat_path_electricity_demand = r'/scripts/templates/switchLoad/D_Pully_10_24_T_I_E_D.dat'

total_electricity_demand, shifted_load_df_electricity, electricity_data, all_values_electricity_demand = process_and_optimize_data_electricity_demand(path_to_load_profile_dat, path_to_excel_file_BAU, model_path_electricity_demand, output_single_column_dat_path_electricity_demand)


# add all values of gwp_profile to get one total value
total_load_profile = load_profile.sum()
print(len(load_profile))
print(total_load_profile)

# add all values of all_values_gwp to get one total value
total_all_values_gwp = sum(all_values_gwp)
print(len(all_values_gwp))
print(total_all_values_gwp)

total_all_values_SH = sum(all_values_gwp)
print(len(all_values_SH))
print(total_all_values_SH)

total_electricity_demand = sum(all_values_electricity_demand)
print(len(all_values_electricity_demand))
print(total_electricity_demand)