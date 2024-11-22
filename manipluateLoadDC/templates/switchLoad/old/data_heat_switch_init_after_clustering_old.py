import pandas as pd
import csv
from datetime import datetime
import amplpy
import matplotlib.pyplot as plt

def process_and_optimize_data_GWP(path_to_load_profile_dat, path_to_emissions, path_timestamp_dat, model_path, output_single_column_dat_path):
    def read_and_process_csv(path_to_load_profile_dat, path_to_emissions):
        # Load profile of data centre after clustering
        load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')

        # Load GWP100a profile from electricity_matrix_2019_reduced.csv
        emissions_matrix = pd.read_csv(path_to_emissions, index_col=[0, 1, 2])
        gwp_row = emissions_matrix.loc[(emissions_matrix.index.get_level_values(2) == 'GWP100a') & (emissions_matrix.index.get_level_values(0) == 'CH')]
        gwp_profile = gwp_row.T
        gwp_profile.index = range(1, len(gwp_profile) + 1)
        gwp_profile.index.name = 'Hour'
        gwp_profile.columns = ['gwp']
        gwp_profile.to_csv('gwp_profile_grid.csv')

        return load_profile, gwp_profile

    def calculate_hour_of_year(timestamp):
        dt = datetime.strptime(timestamp, '%m/%d/%Y/%H')
        new_year_day = datetime(dt.year, 1, 1)
        hour_of_year = int((dt - new_year_day).total_seconds() // 3600)
        return hour_of_year

    def convert_timestamp_to_csv(path_timestamp_dat, path_timestamp_csv):
        with open(path_timestamp_dat, 'r') as dat_file, open(path_timestamp_csv, 'w', newline='') as csv_file:
            reader = csv.reader(dat_file, delimiter='\t')
            writer = csv.writer(csv_file, delimiter=',')

            header = next(reader)
            header.append('HourOfYear')
            writer.writerow(header)

            for row in reader:
                timestamp = row[0]
                hour_of_year = calculate_hour_of_year(timestamp)
                row.append(hour_of_year)
                if len(row) == len(header) - 1:  # Check if Weekday column is missing
                    row.insert(-1, '')  # Insert empty value for Weekday column
                writer.writerow(row)

    def filter_gwp_profile(path_timestamp_csv, path_hourly_gwp_profile, path_filtered_data_gwp_dat):
        days = []
        extreme_hours = []

        with open(path_timestamp_csv, 'r') as timestamp_file:
            reader = csv.DictReader(timestamp_file)
            for row in reader:
                day = row['Day']
                hour_of_year = row.get('HourOfYear')
                if day is not None and hour_of_year is not None:
                    days.append(int(day))
                    extreme_hours.append(int(hour_of_year))

        filtered_values = []
        extreme_values = []

        with open(path_hourly_gwp_profile, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                hour = int(row[0])
                gwp = float(row[1])
                day_of_year = (hour - 1) // 24 + 1
                if day_of_year in days[:-2]:
                    filtered_values.append((day_of_year, gwp))
                if hour in extreme_hours[-2:]:
                    extreme_values.append(gwp)

        # Write the filtered values to the output file in the original order
        with open(path_filtered_data_gwp_dat, 'w') as dat_file:
            for day in days[:-2]:
                for value in filtered_values:
                    if value[0] == day:
                        dat_file.write(f"{value[1]}\n")
            for value in extreme_values:
                dat_file.write(f"{value}\n")

    def optimize_load_profile(path_to_load_profile_dat, path_filtered_data_gwp_dat, output_dat_path, model_path):
        # Load data from filtered_data.dat and gwp_profile_grid.csv
        load_profile = pd.read_csv(path_to_load_profile_dat, header=None, names=['Load_Profile'])
        gwp_profile = pd.read_csv(path_filtered_data_gwp_dat, header=None, names=['gwp'])

        # Determine the number of hours (T)
        T = len(load_profile) - 2  # Exclude the last two hours

        # Save data in AMPL compatible format (dat)
        with open(output_dat_path, 'w') as f:
            f.write(f'param T := {T};\n')
            f.write('param load :=\n')
            for i, load in enumerate(load_profile['Load_Profile'][:T]):  # Exclude the last two hours
                f.write(f'{i + 1} {load}\n')
            f.write(';\n')

            f.write('param objective :=\n')
            for i, objective in enumerate(gwp_profile['gwp'][:T]):  # Exclude the last two hours
                f.write(f'{i + 1} {objective}\n')
            f.write(';\n')

        # AMPL
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')

        # Load model and data
        ampl.read(model_path)

        # Define T in the model before loading data
        ampl.eval(f'let T := {T};')

        ampl.readData(output_dat_path)

        # Run optimisation
        ampl.solve()

        # Show results
        shifted_load = ampl.getVariable('shifted_load').getValues()
        total_gwp = ampl.getObjective('gwp').value()

        # Convert shifted_load to a pandas DataFrame
        shifted_load_df_GWP = shifted_load.toPandas()
        shifted_load_df_GWP.index.name = 'Hour'
        shifted_load_df_GWP.columns = ['Load_Profile']
        shifted_load_df_GWP.reset_index(inplace=True)

        return total_gwp, shifted_load_df_GWP

    def save_optimized_data(shifted_load_df_GWP, extreme_values, output_dat_path):
        with open(output_dat_path, 'w') as dat_file:
            dat_file.write('param load :=\n')
            for i, load in enumerate(shifted_load_df_GWP['Load_Profile']):
                dat_file.write(f'{i + 1} {load}\n')
            dat_file.write(';\n')

            dat_file.write('param gwp :=\n')
            for i in range(len(shifted_load_df_GWP)):
                dat_file.write(f'{i + 1} {shifted_load_df_GWP["Load_Profile"][i]}\n')
            for i in range(len(extreme_values)):
                dat_file.write(f'{len(shifted_load_df_GWP) + i + 1} {extreme_values[i]}\n')
            dat_file.write(';\n')

    def save_single_column_dat(data, output_path):
        with open(output_path, 'w') as dat_file:
            for value in data:
                dat_file.write(f"{value}\n")

    # Main execution
    load_profile, gwp_profile = read_and_process_csv(path_to_load_profile_dat, path_to_emissions)

    path_timestamp_csv = r'C:\Users\there\Desktop\REHO2\scripts\templates\switchLoad\timestamp_with_hour_of_year.csv'
    convert_timestamp_to_csv(path_timestamp_dat, path_timestamp_csv)

    path_hourly_gwp_profile = r'C:\Users\there\Desktop\REHO2\scripts\templates\switchLoad\gwp_profile_grid.csv'
    path_filtered_data_gwp_dat = r'C:\Users\there\Desktop\REHO2\scripts\templates\switchLoad\filtered_data_gwp.dat'
    filter_gwp_profile(path_timestamp_csv, path_hourly_gwp_profile, path_filtered_data_gwp_dat)

    # Optimize load profile excluding the last two hours (extreme values)
    path_output_dat_before_optimization = 'data_switch_GWP_before_optimization.dat'
    total_gwp, shifted_load_df_GWP = optimize_load_profile(path_to_load_profile_dat, path_filtered_data_gwp_dat, path_output_dat_before_optimization, model_path)

    # Save the optimized data including the extreme values
    extreme_values = [float(line.strip()) for line in open(path_filtered_data_gwp_dat).readlines()[-2:]]
    output_dat_path_after_optimization = 'data_switch_GWP_after_optimization.dat'
    save_optimized_data(shifted_load_df_GWP, extreme_values, output_dat_path_after_optimization)

    # Save all values in a single column to the specified path
    all_values = shifted_load_df_GWP['Load_Profile'].tolist() + extreme_values
    save_single_column_dat(all_values, output_single_column_dat_path)

    return total_gwp, shifted_load_df_GWP, gwp_profile


# write function for optimising with same principle but with regards to Space heating instead GWP given as profile in space_heating_BAU_GWP
def process_and_optimize_data_space_heating(path_to_load_profile_dat, path_to_SH_profile_dat, model_path_SH, output_single_column_dat_path):
    def extract_and_save_data(excel_file):
        # Definierte Parameter innerhalb der Funktion
        sheet_name = 'df_Buildings_t'
        column_name = 'House_Q_heating'
        output_dat_file = 'space_heating_BAU_GWP.dat'

        # Load the Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=[column_name])

        # Extract the data from the column
        heating_data = df[column_name].tolist()

        # Write the data to a .dat file
        with open(output_dat_file, 'w') as f:
            for value in heating_data:
                f.write(f"{value}\n")

    def read_and_process_csv(path_to_load_profile_dat, path_to_SH_profile_dat):
        # Load profile of data centre after clustering
        load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')

        # Load Space heating profile from BAU_GWP
        SH_profile = pd.read_csv(path_to_SH_profile_dat, sep='\t', header=None, engine='python')

        return load_profile, SH_profile

    def optimize_load_profile(path_to_load_profile_dat, path_to_SH_profile_dat, output_dat_path, model_path):
        # Load data from filtered_data.dat and space_heating_BAU_GWP.dat
        load_profile = pd.read_csv(path_to_load_profile_dat, header=None, names=['Load_Profile'])
        SH_profile = pd.read_csv(path_to_SH_profile_dat, header=None, names=['SH'])

        # Determine the number of hours (T)
        T = len(load_profile) - 2

        # Save data in AMPL compatible format (dat)
        with open(output_dat_path, 'w') as f:
            f.write(f'param T := {T};\n')
            f.write('param load :=\n')
            for i, load in enumerate(load_profile['Load_Profile'][:T]):  # Exclude the last two hours
                f.write(f'{i + 1} {load}\n')
            f.write(';\n')

            f.write('param objective :=\n')
            for i, objective in enumerate(SH_profile['SH'][:T]):  # Exclude the last two hours
                f.write(f'{i + 1} {objective}\n')
            f.write(';\n')

        # AMPL
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')

        # Load model and data
        ampl.read(model_path)

        # Define T in the model before loading data
        ampl.eval(f'let T := {T};')

        ampl.readData(output_dat_path)

        # Run optimisation
        ampl.solve()

        # Show results
        shifted_load = ampl.getVariable('shifted_load').getValues()
        total_SH = ampl.getObjective('use').value()

        # Convert shifted_load to a pandas DataFrame
        shifted_load_df_SH = shifted_load.toPandas()
        shifted_load_df_SH.index.name = 'Hour'
        shifted_load_df_SH.columns = ['Load_Profile']
        shifted_load_df_SH.reset_index(inplace=True)

        return total_SH, shifted_load_df_SH

    def save_optimized_data(shifted_load_df_SH, extreme_values, output_dat_path):
        with open(output_dat_path, 'w') as dat_file:
            dat_file.write('param load :=\n')
            for i, load in enumerate(shifted_load_df_SH['Load_Profile']):
                dat_file.write(f'{i + 1} {load}\n')
            dat_file.write(';\n')

            dat_file.write('param SH :=\n')
            for i in range(len(shifted_load_df_SH)):
                dat_file.write(f'{i + 1} {shifted_load_df_SH["Load_Profile"][i]}\n')
            for i in range(len(extreme_values)):
                dat_file.write(f'{len(shifted_load_df_SH) + i + 1} {extreme_values[i]}\n')
            dat_file.write(';\n')

    def save_single_column_dat(data, output_path):
        with open(output_path, 'w') as dat_file:
            for value in data:
                dat_file.write(f"{value}\n")

    # Main execution
    path_to_excel_file_BAU = r'/scripts/template/results/ALL_EPFL_BAU_gwp.xlsx'
    extract_and_save_data(path_to_excel_file_BAU)
    load_profile, SH_profile = read_and_process_csv(path_to_load_profile_dat, path_to_SH_profile_dat)

    # Optimize load profile excluding the last two hours (extreme values)
    path_output_dat_before_optimization = 'data_switch_SH_before_optimization.dat'
    total_SH, shifted_load_df_SH = optimize_load_profile(path_to_load_profile_dat, path_to_SH_profile_dat, path_output_dat_before_optimization, model_path_SH)

    # Save the optimized data including the extreme values
    extreme_values = [float(line.strip()) for line in open(path_to_SH_profile_dat).readlines()[-2:]]
    output_dat_path_after_optimization = 'data_switch_SH_after_optimization.dat'
    save_optimized_data(shifted_load_df_SH, extreme_values, output_dat_path_after_optimization)

    # Save all values in a single column to the specified path
    all_values = shifted_load_df_SH['Load_Profile'].tolist() + extreme_values
    save_single_column_dat(all_values, output_single_column_dat_path)

    return total_SH, shifted_load_df_SH, SH_profile


#write function for optimising with same principle but with regards to electricity demand instead GWP given as profile in electricity_demand_BAU_GWP
def process_and_optimize_data_electricity_demand(path_to_load_profile_dat, path_to_electricity_profile_dat, model_path_electricity, output_single_column_dat_path):
    def extract_and_save_data(excel_file):
        # Define parameters within the function
        sheet_name = 'df_Buildings_t'
        column_name = 'Domestic_electricity'
        output_dat_file = 'electricity_demand_BAU_GWP.dat'

        # Load the Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=[column_name])

        # Extract the data from the column
        electricity_data = df[column_name].tolist()

        # Write the data to a .dat file
        with open(output_dat_file, 'w') as f:
            for value in electricity_data:
                f.write(f"{value}\n")

    def read_and_process_csv(path_to_load_profile_dat, path_to_electricity_profile_dat):
        # Load profile of data centre after clustering
        load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')

        # Load Electricity profile from electricity_demand_BAU_GWP.dat
        electricity_profile = pd.read_csv(path_to_electricity_profile_dat, sep='\t', header=None, engine='python')

        return load_profile, electricity_profile

    def optimize_load_profile(path_to_load_profile_dat, path_to_electricity_profile_dat, output_dat_path, model_path):
        # Load data from filtered_data.dat and electricity_demand_BAU_GWP.dat
        load_profile = pd.read_csv(path_to_load_profile_dat, header=None, names=['Load_Profile'])
        electricity_profile = pd.read_csv(path_to_electricity_profile_dat, header=None, names=['electricity'])

        # Determine the number of hours (T)
        T = len(load_profile) - 2

        # Save data in AMPL compatible format (dat)
        with open(output_dat_path, 'w') as f:
            f.write(f'param T := {T};\n')
            f.write('param load :=\n')
            for i, load in enumerate(load_profile['Load_Profile'][:T]):  # Exclude the last two hours
                f.write(f'{i + 1} {load}\n')
            f.write(';\n')

            f.write('param objective :=\n')
            for i, objective in enumerate(electricity_profile['electricity'][:T]):  # Exclude the last two hours
                f.write(f'{i + 1} {objective}\n')
            f.write(';\n')

        # AMPL
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')

        # Load model and data
        ampl.read(model_path)

        # Define T in the model before loading data
        ampl.eval(f'let T := {T};')

        ampl.readData(output_dat_path)

        # Run optimisation
        ampl.solve()

        # Show results
        shifted_load = ampl.getVariable('shifted_load').getValues()
        total_electricity_demand = ampl.getObjective('use').value()

        # Convert shifted_load to a pandas DataFrame
        shifted_load_df_electricity = shifted_load.toPandas()
        shifted_load_df_electricity.index.name = 'Hour'
        shifted_load_df_electricity.columns = ['Load_Profile']
        shifted_load_df_electricity.reset_index(inplace=True)

        return total_electricity_demand, shifted_load_df_electricity

    def save_optimized_data(shifted_load_df_electricity, extreme_values, output_dat_path):
        with open(output_dat_path, 'w') as dat_file:
            dat_file.write('param load :=\n')
            for i, load in enumerate(shifted_load_df_electricity['Load_Profile']):
                dat_file.write(f'{i + 1} {load}\n')
            dat_file.write(';\n')

            dat_file.write('param electricity :=\n')
            for i in range(len(shifted_load_df_electricity)):
                dat_file.write(f'{i + 1} {shifted_load_df_electricity["Load_Profile"][i]}\n')
            for i in range(len(extreme_values)):
                dat_file.write(f'{len(shifted_load_df_electricity) + i + 1} {extreme_values[i]}\n')
            dat_file.write(';\n')

    def save_single_column_dat(data, output_path):
        with open(output_path, 'w') as dat_file:
            for value in data:
                dat_file.write(f"{value}\n")

    # Main execution
    load_profile, electricity_profile = read_and_process_csv(path_to_load_profile_dat, path_to_electricity_profile_dat)

    # Optimize load profile excluding the last two hours (extreme values)
    path_output_dat_before_optimization = 'data_switch_electricity_before_optimization.dat'
    total_electricity_demand, shifted_load_df_electricity = optimize_load_profile(path_to_load_profile_dat, path_to_electricity_demand_profile_dat, path_output_dat_before_optimization, model_path_electricity_demand)

    # Save the optimized data including the extreme values
    extreme_values = [float(line.strip()) for line in open(path_to_electricity_profile_dat).readlines()[-2:]]
    output_dat_path_after_optimization = 'data_switch_electricity_after_optimization.dat'
    save_optimized_data(shifted_load_df_electricity, extreme_values, output_dat_path_after_optimization)

    # Save all values in a single column to the specified path
    all_values = shifted_load_df_electricity['Load_Profile'].tolist() + extreme_values
    save_single_column_dat(all_values, output_single_column_dat_path)

    return total_electricity_demand, shifted_load_df_electricity, electricity_profile

# example for calling function of GWP
path_to_load_profile_dat = r'/scripts/templates/data/clustering/D_Pully_10_24_T_I_E_D.dat'
load_profile = pd.read_csv(path_to_load_profile_dat, sep='\t', header=None, engine='python')
path_to_emissions = r'/reho/data/emissions/electricity_matrix_2019_reduced.csv'
path_timestamp_dat = r'/scripts/template/data/clustering/timestamp_Pully_10_24_T_I_E_D.dat'
model_path_gwp = r'/scripts/templates/switchLoad/afterClustering/data_heat_switch_after_clustering_gwp.mod'
output_single_column_dat_path_GWP = r'/scripts/templates/switchLoad/D_Pully_10_24_T_I_E_D.dat'

total_gwp, shifted_load_df_GWP,gwp_profile = process_and_optimize_data_GWP(path_to_load_profile_dat, path_to_emissions, path_timestamp_dat, model_path_gwp, output_single_column_dat_path_GWP)

# example for calling function of SH
path_to_load_profile_dat = r'/scripts/templates/data/clustering/D_Pully_10_24_T_I_E_D.dat'
path_to_SH_profile_dat = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\switchLoad\\space_heating_BAU_GWP.dat'
model_path_SH = r'/scripts/templates/switchLoad/afterClustering/data_heat_switch_after_clustering_use.mod'
output_single_column_dat_path_SH = r'/scripts/templates/switchLoad/D_Pully_10_24_T_I_E_D.dat'

total_SH, shifted_load_df_SH,SH_profile = process_and_optimize_data_space_heating(path_to_load_profile_dat, path_to_SH_profile_dat, model_path_SH, output_single_column_dat_path_SH)

# example for calling function of Electricity demand
path_to_load_profile_dat = r'/scripts/templates/data/clustering/D_Pully_10_24_T_I_E_D.dat'
path_to_electricity_demand_profile_dat = r'C:\Users\there\Desktop\REHO2\scripts\templates\switchLoad\electricity_demand_BAU_GWP.dat'
model_path_electricity_demand = r'/scripts/templates/switchLoad/afterClustering/data_heat_switch_after_clustering_use.mod'
output_single_column_dat_path_electricity_demand = r'/scripts/templates/switchLoad/D_Pully_10_24_T_I_E_D.dat'

total_electricity_demand, shifted_load_df_electricity, electricity_profile = process_and_optimize_data_electricity_demand(path_to_load_profile_dat, path_to_electricity_demand_profile_dat, model_path_electricity_demand, output_single_column_dat_path_electricity_demand)


### plotting
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_GWP['Hour'][:242], shifted_load_df_GWP['Load_Profile'][:242], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile[:242], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax2 = ax1.twinx()
ax2.plot(gwp_profile[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='GWP')
ax2.set_ylabel('GWP', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
filename = 'shifted_load_week_comparison_GWP_grid_vs_original.png'
plt.show()


# create same plot but for SH
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_SH['Hour'][:242], shifted_load_df_SH['Load_Profile'][:242], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile[:242], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax2 = ax1.twinx()
ax2.plot(SH_profile[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='SH')
ax2.set_ylabel('SH', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
filename = 'shifted_load_week_comparison_SH_vs_original.png'
plt.show()

# create same plot but for Electricity demand
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_electricity['Hour'][:242], shifted_load_df_electricity['Load_Profile'][:242], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile[:242], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax2 = ax1.twinx()
ax2.plot(electricity_profile[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='Electricity Demand')
ax2.set_ylabel('Electricity Demand', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
filename = 'shifted_load_week_comparison_electricity_demand_vs_original.png'
plt.show()

