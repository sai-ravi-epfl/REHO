import pandas as pd
import amplpy
import matplotlib.pyplot as plt

def process_and_optimize_data_GWP(path_to_load_profile, path_to_emissions, model_path, output_path, size=288):
    def read_and_process_dat(path_to_load_profile, path_to_emissions):
        # Load profile of data centre before clustering which is as csv file
        load_profile = pd.read_csv(path_to_load_profile)
        load_profile = load_profile['Load_Profile'].values  # Extract the Load_Profile column as a numpy array


        # Load GWP100a profile from electricity_matrix_2019_reduced.csv
        emissions_matrix = pd.read_csv(path_to_emissions, index_col=[0, 1, 2])
        gwp_row = emissions_matrix.loc[(emissions_matrix.index.get_level_values(2) == 'GWP100a') & (emissions_matrix.index.get_level_values(0) == 'CH')]
        gwp_profile = gwp_row.T
        gwp_profile.index = range(1, len(gwp_profile) + 1)
        gwp_profile.index.name = 'Hour'
        gwp_profile.columns = ['gwp']
        return load_profile, gwp_profile


    def optimize_load_profile(load_profile, filtered_gwp_profile, model_path, size=288):
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.read(model_path)
        ampl.eval(f'let size := {size};')
        T = 8760

        load_data = {i + 1: load for i, load in enumerate(load_profile[:T])}
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

    def save_load_profile(shifted_load, output_path):
        shifted_load.to_csv(output_path, sep=',', index=False, header=True)

    load_profile, gwp_profile = read_and_process_dat(path_to_load_profile, path_to_emissions)

    total_gwp, shifted_load_df_GWP = optimize_load_profile(load_profile, gwp_profile, model_path)

    save_load_profile(shifted_load_df_GWP, output_path)

    return total_gwp, shifted_load_df_GWP, gwp_profile



def extract_data_and_periods(excel_file, column_name):
    sheet_name = 'df_Buildings_t'  # Sheet name
    df = pd.read_excel(excel_file, sheet_name=sheet_name)  # Load the specified sheet from the Excel file
    df.dropna(subset=[column_name], inplace=True)  # Drop rows with NaN values in the specified column
    csv_rows = [[index + 1, row[column_name]] for index, row in df.iterrows()]  # Add index + 1 as HourOfYear
    csv_df = pd.DataFrame(csv_rows, columns=['HourOfYear', column_name])  # Convert the list of rows to a DataFrame
    periods, time_of_year = [], []  # Initialize lists for periods and time_of_year
    num_full_days = len(csv_df) // 24  # Calculate the number of full days
    for day in range(1, num_full_days + 1):  # Iterate over each day
        for hour in range(1, 25):  # Iterate over each hour
            periods.append(day)
            time_of_year.append(hour)
    remaining_hours = len(csv_df) - num_full_days * 24  # Calculate remaining hours
    for hour in range(1, remaining_hours + 1):  # Add remaining periods for extreme periods (11 and 12)
        periods.extend([11, 12])
        time_of_year.extend([hour, hour])
    while len(periods) < len(csv_df):  # Ensure that the lengths of periods and time_of_year match the length of csv_df
        periods.append(12)
        time_of_year.append(len(time_of_year) % 24 + 1)
    csv_df['PeriodOfYear'], csv_df['TimeOfYear'] = periods[:len(csv_df)], time_of_year[:len(
        csv_df)]  # Add PeriodOfYear and TimeOfYear columns
    return csv_df[['HourOfYear', 'PeriodOfYear', column_name]]  # Reorder columns


def extract_index(excel_file):
    return pd.read_excel(excel_file, sheet_name='df_Index',
                         usecols=['HourOfYear', 'PeriodOfYear'])  # Load the Excel file


def merge_dataframes(df_index, df_data, column_name):
    load_profile_list = []  # Initialize an empty list to store the rows for the DataFrame
    for _, row in df_index.iterrows():  # Iterate over each row in the index file
        period_of_year = row['PeriodOfYear']
        data_values_for_period = df_data[
            df_data['PeriodOfYear'] == period_of_year]  # Filter data values for the current period
        if not data_values_for_period.empty:
            hour_of_year = row['HourOfYear']
            data_value = data_values_for_period.iloc[(hour_of_year - 1) % len(data_values_for_period)][column_name]
            load_profile_list.append(
                {'HourOfYear': hour_of_year, 'PeriodOfYear': period_of_year, column_name: data_value})
    return pd.DataFrame(load_profile_list)  # Convert the list to a DataFrame


def process_and_optimize_data(path_to_load_profile, path_to_excel_file_BAU, model_path, output_path, column_name,
                              size=288):
    load_profile = pd.read_csv(path_to_load_profile)[
        'Load_Profile'].values  # Load profile of data centre after clustering
    df_data = extract_data_and_periods(path_to_excel_file_BAU, column_name)  # Extract data and periods from Excel file
    df_index = extract_index(path_to_excel_file_BAU)  # Extract index file from Excel file
    profile_data_df = merge_dataframes(df_index, df_data, column_name)  # Merge dataframes based on index and periods
    profile_data = profile_data_df[column_name].tolist()  # Convert profile data to list

    ampl = amplpy.AMPL()  # Initialize AMPL instance
    ampl.setOption('solver', 'gurobi')  # Set solver option to Gurobi
    ampl.read(model_path)  # Read AMPL model file
    ampl.eval(f'let size := {size};')  # Set size parameter

    T = 8760
    load_data = {i + 1: load for i, load in enumerate(load_profile[:T])}  # Create load data dictionary
    profile_data_dict = {i + 1: data for i, data in enumerate(profile_data[:T])}  # Create profile data dictionary

    ampl.param['load'] = load_data  # Set load parameter in AMPL
    ampl.param['objective'] = profile_data_dict  # Set objective parameter in AMPL
    ampl.solve()  # Solve the optimization problem

    shifted_load = ampl.getVariable('shifted_load').getValues().toPandas()  # Get shifted load values as DataFrame
    shifted_load.index.name = 'Hour'
    shifted_load.columns = ['Load_Profile']
    shifted_load.reset_index(inplace=True)

    total_use = ampl.getObjective('use').value()  # Get total use value

    shifted_load.to_csv(output_path, sep=',', index=False, header=True)  # Save shifted load DataFrame to CSV file

    return total_use, shifted_load, profile_data

# Example call for GWP
path_to_data_centre_heat_profile = r'C:\Users\there\Desktop\REHO2\scripts\templates\yearly_data_centre_profile_repeated2.csv'
path_to_emissions = r'C:\Users\there\Desktop\REHO2\reho\data\emissions\electricity_matrix_2019_reduced.csv'
model_path = r'C:\Users\there\Desktop\REHO2\scripts\templates\switchLoad\data_heat_switch_before_clustering_gwp.mod'
size = 288
output_path = r'C:\Users\there\Desktop\REHO2\scripts\templates\yearly_data_centre_profile_repeated3.csv'

total_gwp, shifted_load_df_GWP, gwp_profile = process_and_optimize_data_GWP(path_to_data_centre_heat_profile, path_to_emissions, model_path, output_path, size)

# Example call for Q_heating
path_to_load_profile = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\yearly_data_centre_profile_repeated2.csv'
path_to_excel_file_BAU = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_gwp.xlsx'
model_path_SH = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\switchLoad\\data_heat_switch_before_clustering_use.mod'
output_path_SH = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\yearly_data_centre_profile_repeated4.csv'

total_SH, shifted_load_df_SH, heating_data = process_and_optimize_data(path_to_load_profile, path_to_excel_file_BAU,
                                                                       model_path_SH, output_path_SH, 'House_Q_heating')

# Example call for Domestic_electricity
model_path_electricity = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\switchLoad\\data_heat_switch_before_clustering_use.mod'
output_path_electricity = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\yearly_data_centre_profile_repeated5.csv'

total_electricity, shifted_load_df_electricity, electricity_data = process_and_optimize_data(path_to_load_profile,
                                                                                             path_to_excel_file_BAU,
                                                                                             model_path_electricity,
                                                                                             output_path_electricity,
                                                                                             'Domestic_electricity')

# Plotting for GWP
load_profile = pd.read_csv(path_to_data_centre_heat_profile)
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_GWP['Hour'][:242], shifted_load_df_GWP['Load_Profile'][:242], linestyle='-', marker='',
         color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:242], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(0, 242)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(gwp_profile[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='GWP')
ax2.set_ylim(bottom=0)
ax2.set_ylabel('GWP', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
filename = 'shifted_load_week_comparison_GWP_grid_vs_original.png'
plt.show()


# Plotting for SH
load_profile = pd.read_csv(path_to_load_profile)
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_SH['Hour'][:242], shifted_load_df_SH['Load_Profile'][:242], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:242], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(0, 242)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(heating_data[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='Space heating')
ax2.set_ylim(min(heating_data[:242]), max(heating_data[:242]) * 1.1)  # Add some space above the maximum value
ax2.set_ylabel('Space heating demand [kW]', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
plt.show()

# Plotting for Domestic_electricity
load_profile = pd.read_csv(path_to_load_profile)
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_electricity['Hour'][:242], shifted_load_df_electricity['Load_Profile'][:242], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:242], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(0, 242)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(electricity_data[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='Electricity')
ax2.set_ylim(min(electricity_data[:242]), max(electricity_data[:242]) * 1.1)  # Add some space above the maximum value
ax2.set_ylabel('Electricity demand [kW]', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
plt.show()
