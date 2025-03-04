import pandas as pd
import amplpy
import matplotlib.pyplot as plt

def process_and_optimize_data_GWP(path_to_load_profile, path_to_emissions, model_path, output_path, size=288):
    def read_and_process_dat(path_to_load_profile, path_to_emissions):
        # Load profile of data centre before clustering which is as csv file
        load_profile = pd.read_csv(path_to_load_profile)
        load_profile = load_profile['Load_Profile'].values  # Extract the Load_Profile column as a numpy array

        # Load GWP100a profile from Elec_CO2_2023.txt
        gwp_profile = pd.read_csv(path_to_emissions, sep=',', header=None)
        gwp_profile.columns = ['Hour', 'gwp']
        gwp_profile.set_index('Hour', inplace=True)
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

    total_gwp, shifted_load_df_GWP = optimize_load_profile(load_profile, gwp_profile, model_path, size)

    save_load_profile(shifted_load_df_GWP, output_path)

    return total_gwp, shifted_load_df_GWP, gwp_profile


def extract_data_and_periods(excel_file, column_name, additional_sheet=None, additional_column=None, filter_value=None):
    sheet_name = 'df_Buildings_t'
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df.dropna(subset=[column_name], inplace=True)
    print("Initial DataFrame:", df.head())  # Debugging output

    if additional_sheet and additional_column and filter_value:
        df_additional = pd.read_excel(excel_file, sheet_name=additional_sheet)
        print("Additional DataFrame before filtering:", df_additional.head())  # Debugging output

        # Fill missing values in 'Layer' and 'Unit' columns with the previous value
        df_additional['Layer'] = df_additional['Layer'].fillna(method='ffill')
        df_additional['Unit'] = df_additional['Unit'].fillna(method='ffill')

        # Filter the additional data based on the filter_value
        df_additional = df_additional[(df_additional['Layer'] == 'Electricity') & (df_additional['Unit'] == filter_value)]
        print("Filtered Additional DataFrame:", df_additional.head())  # Debugging output

        # Fill missing 'Time' and additional_column values with 0
        df_additional['Time'] = df_additional['Time'].fillna(0)
        df_additional[additional_column] = df_additional[additional_column].fillna(0)

        if 'HourOfYear' not in df.columns:
            df['HourOfYear'] = range(1, len(df) + 1)

        if 'HourOfYear' not in df_additional.columns:
            df_additional['HourOfYear'] = range(1, len(df_additional) + 1)

        df_additional.set_index('HourOfYear', inplace=True)
        df.set_index('HourOfYear', inplace=True)

        # Reindex and fill missing values with 0
        df_additional = df_additional.reindex(df.index).fillna(0)
        print("Reindexed Additional DataFrame:", df_additional.head())  # Debugging output

        # Add the additional column values to the main dataframe column
        df[column_name] += df_additional[additional_column]
        print("Updated DataFrame with added values:", df[[column_name]].head())  # Debugging output

    csv_rows = [[index + 1, row[column_name]] for index, row in df.iterrows()]
    csv_df = pd.DataFrame(csv_rows, columns=['HourOfYear', column_name])
    periods, time_of_year = [], []
    num_full_days = len(csv_df) // 24
    for day in range(1, num_full_days + 1):
        for hour in range(1, 25):
            periods.append(day)
            time_of_year.append(hour)
    remaining_hours = len(csv_df) - num_full_days * 24
    for hour in range(1, remaining_hours + 1):
        periods.extend([11, 12])
        time_of_year.extend([hour, hour])
    while len(periods) < len(csv_df):
        periods.append(12)
        time_of_year.append(len(time_of_year) % 24 + 1)
    csv_df['PeriodOfYear'], csv_df['TimeOfYear'] = periods[:len(csv_df)], time_of_year[:len(csv_df)]
    return csv_df[['HourOfYear', 'PeriodOfYear', column_name]]

def extract_index(excel_file):
    return pd.read_excel(excel_file, sheet_name='df_Index', usecols=['HourOfYear', 'PeriodOfYear'])

def merge_dataframes(df_index, df_data, column_name):
    load_profile_list = []
    for _, row in df_index.iterrows():
        period_of_year = row['PeriodOfYear']
        data_values_for_period = df_data[df_data['PeriodOfYear'] == period_of_year]
        if not data_values_for_period.empty:
            hour_of_year = row['HourOfYear']
            data_value = data_values_for_period.iloc[(hour_of_year - 1) % len(data_values_for_period)][column_name]
            load_profile_list.append({'HourOfYear': hour_of_year, 'PeriodOfYear': period_of_year, column_name: data_value})
    return pd.DataFrame(load_profile_list)

def process_and_optimize_data(path_to_load_profile, path_to_excel_file_BAU, model_path, output_path, column_name, size=288, additional_sheet=None, additional_column=None, filter_value=None):
    load_profile = pd.read_csv(path_to_load_profile)['Load_Profile'].values
    df_data = extract_data_and_periods(path_to_excel_file_BAU, column_name, additional_sheet=additional_sheet, additional_column=additional_column, filter_value=filter_value)
    df_index = extract_index(path_to_excel_file_BAU)
    profile_data_df = merge_dataframes(df_index, df_data, column_name)
    # save profile data as csv
    profile_data_df.to_csv(r'profile_data.csv', index=False)
    profile_data = profile_data_df[column_name].tolist()

    ampl = amplpy.AMPL()
    ampl.setOption('solver', 'gurobi')
    ampl.read(model_path)
    ampl.eval(f'let size := {size};')

    T = 8760
    load_data = {i + 1: load for i, load in enumerate(load_profile[:T])}
    profile_data_dict = {i + 1: data for i, data in enumerate(profile_data[:T])}

    ampl.param['load'] = load_data
    ampl.param['objective'] = profile_data_dict
    ampl.solve()

    shifted_load = ampl.getVariable('shifted_load').getValues().toPandas()
    shifted_load.index.name = 'Hour'
    shifted_load.columns = ['Load_Profile']
    shifted_load.reset_index(inplace=True)

    total_use = ampl.getObjective('use').value()

    shifted_load.to_csv(output_path, sep=',', index=False, header=True)

    return total_use, shifted_load, profile_data_df

'''
# Example call for GWP
path_to_load_profile = r'/manipluateLoadDC/yearly_data_centre_profile_repeated2.csv'
path_to_emissions = r'/reho/data/weather/Elec_CO2_2023.txt'
model_path = r'/manipluateLoadDC/template_Theresa/switchLoad/beforeClustering/data_heat_switch_before_clustering_gwp.mod'
size = 288
output_path = r'/manipluateLoadDC/template_Theresa/profiles/yearly_data_centre_profile_repeated13.csv'

total_gwp, shifted_load_df_GWP, gwp_profile = process_and_optimize_data_GWP(path_to_load_profile, path_to_emissions, model_path, output_path, size)

# Example call for Q_heating
path_to_excel_file_BAU = r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_BAU_168h_50kW_gwp.xlsx'
model_path_use = r'/manipluateLoadDC/template_Theresa/switchLoad/beforeClustering/data_heat_switch_before_clustering_use.mod'
output_path_SH = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\yearly_data_centre_profile_repeated14.csv'

total_SH, shifted_load_df_SH, heating_data_df = process_and_optimize_data(path_to_load_profile, path_to_excel_file_BAU, model_path_use, output_path_SH, 'House_Q_heating', size)


# Example call for Domestic_electricity
output_path_electricity = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\templates\\yearly_data_centre_profile_repeated15.csv'

total_electricity, shifted_load_df_electricity, electricity_data_df = process_and_optimize_data(path_to_load_profile, path_to_excel_file_BAU, model_path_use, output_path_electricity, 'Domestic_electricity',size, additional_sheet='df_Unit_t', additional_column='Units_demand', filter_value='HeatPump_Geothermal_district')


# Plotting for GWP
load_profile = pd.read_csv(path_to_load_profile)
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_GWP['Hour'][:168], shifted_load_df_GWP['Load_Profile'][:168], linestyle='-', marker='',
         color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:168], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hour of the year', fontsize=14)
ax1.set_ylabel('Load DC [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(0, 168)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(gwp_profile[:168], linestyle='-', marker='', color='g', linewidth=1.5, label='GWP')
ax2.set_ylim(bottom=0)
ax2.set_ylabel('GWP [gCo2-eq/kWh]', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
filename = 'shifted_load_week_comparison_GWP_grid_vs_original_percentage.png'
plt.show()
fig.savefig(filename, dpi=300)

# Plotting for SH
# Convert the 'Space_heating' column to numeric
heating_data_df['House_Q_heating'] = pd.to_numeric(heating_data_df['House_Q_heating'])
load_profile = pd.read_csv(path_to_load_profile)
# Plotting for SH (3000 to 3168 hours range)
heating_data_df['House_Q_heating'] = pd.to_numeric(heating_data_df['House_Q_heating'])
fig, ax1 = plt.subplots(figsize=(12, 6))
start_hour = 2400
end_hour = start_hour + 168
ax1.plot(shifted_load_df_SH['Hour'][start_hour:end_hour], shifted_load_df_SH['Load_Profile'][start_hour:end_hour], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][start_hour:end_hour], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hour of the year', fontsize=14)
ax1.set_ylabel('Load DC [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(start_hour, end_hour)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(heating_data_df['HourOfYear'][start_hour:end_hour], heating_data_df['House_Q_heating'][start_hour:end_hour], linestyle='-', marker='', color='g', linewidth=1.5, label='Space heating')
ax2.set_ylim(min(heating_data_df['House_Q_heating'][start_hour:end_hour]), max(heating_data_df['House_Q_heating'][start_hour:end_hour]) * 1.1)
ax2.set_ylabel('Space heating demand [kW]', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
plt.show()
fig.savefig('shifted_load_week_comparison_SH_grid_vs_original_percentage.png', dpi=300)

# Shift the green graph (electricity data) to the right by one unit
electricity_data_df['Domestic_electricity'] = electricity_data_df['Domestic_electricity'].shift(1)

# Remove NaN values that result from shifting
electricity_data_df = electricity_data_df.dropna(subset=['Domestic_electricity'])

# Plotting the graphs
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_electricity['Hour'][:168], shifted_load_df_electricity['Load_Profile'][:168], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:168], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hour of the year', fontsize=14)
ax1.set_ylabel('Load DC [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(0, 168)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(electricity_data_df['Domestic_electricity'][:168], linestyle='-', marker='', color='g', linewidth=1.5, label='Electricity')
ax2.set_ylim(min(electricity_data_df['Domestic_electricity'][:168]), max(electricity_data_df['Domestic_electricity'][:168]) * 1.1)  # Add some space above the maximum value
ax2.set_ylabel('Electricity demand [kW]', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
plt.show()
fig.savefig('shifted_load_week_comparison_electricity_grid_vs_original_percentage.png', dpi=300)
'''