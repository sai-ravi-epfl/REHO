import pandas as pd
import csv
from datetime import datetime
import amplpy
import numpy as np
import matplotlib.pyplot as plt


def extract_q_heating_and_periods(excel_file):
    sheet_name = 'df_Buildings_t'

    # Load the specified sheet from the Excel file
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Drop rows with NaN values in 'House_Q_heating'
    df.dropna(subset=['House_Q_heating'], inplace=True)

    # Initialize an empty list to store the rows for the DataFrame
    csv_rows = []

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        heating_value = row['House_Q_heating']
        csv_rows.append([index + 1, heating_value])  # Add index + 1 as HourOfYear

    # Convert the list of rows to a DataFrame
    csv_df = pd.DataFrame(csv_rows, columns=['HourOfYear', 'House_Q_heating'])

    # Add PeriodOfYear and TimeOfYear columns
    periods = []
    time_of_year = []

    num_full_days = len(csv_df) // 24
    for day in range(1, num_full_days + 1):
        for hour in range(1, 25):
            periods.append(day)
            time_of_year.append(hour)

    # Add remaining periods for extreme periods (11 and 12)
    remaining_hours = len(csv_df) - num_full_days * 24
    for hour in range(1, remaining_hours + 1):
        periods.append(11)
        time_of_year.append(hour)

    for hour in range(1, remaining_hours + 1):
        periods.append(12)
        time_of_year.append(hour)

    # Ensure that the lengths of periods and time_of_year match the length of csv_df
    while len(periods) < len(csv_df):
        periods.append(12)
        time_of_year.append(len(time_of_year) % 24 + 1)

    csv_df['PeriodOfYear'] = periods[:len(csv_df)]
    csv_df['TimeOfYear'] = time_of_year[:len(csv_df)]

    # Reorder columns to have HourOfYear, PeriodOfYear, and House_Q_heating
    csv_df = csv_df[['HourOfYear', 'PeriodOfYear', 'House_Q_heating']]

    return csv_df


def extract_index(excel_file):
    sheet_name = 'df_Index'
    columns = ['HourOfYear', 'PeriodOfYear']

    # Load the Excel file
    df_index = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=columns)

    return df_index


def merge_dataframes_and_save(df_index, df_heating_periods):
    # Create a list for the load profile SH
    load_profile_sh_list = []

    # Iterate over each row in the index file and add the corresponding Q_heating values
    for index, row in df_index.iterrows():
        period_of_year = row['PeriodOfYear']

        # Filter heating values for the current period
        heating_values_for_period = df_heating_periods[df_heating_periods['PeriodOfYear'] == period_of_year]

        if not heating_values_for_period.empty:
            hour_of_year = row['HourOfYear']
            heating_value = heating_values_for_period.iloc[(hour_of_year - 1) % len(heating_values_for_period)][
                'House_Q_heating']

            load_profile_sh_list.append({
                'HourOfYear': hour_of_year,
                'PeriodOfYear': period_of_year,
                'House_Q_heating': heating_value
            })

    # Convert the list to a DataFrame
    load_profile_sh = pd.DataFrame(load_profile_sh_list)

    return load_profile_sh


def process_and_optimize_data_space_heating(path_to_load_profile, path_to_excel_file_BAU, model_path_SH, output_path,
                                            size=288):
    def read_and_process_csv(path_to_load_profile):
        # Load profile of data centre after clustering
        load_profile = pd.read_csv(path_to_load_profile)
        load_profile = load_profile['Load_Profile'].values  # Extract the Load_Profile column as a numpy array

        return load_profile

    def optimize_load_profile(load_profile, SH_profile, model_path):
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.read(model_path)
        ampl.eval(f'let size := {size};')
        T = 8760

        load_data = {i + 1: load for i, load in enumerate(load_profile[:T])}
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

    def save_load_profile(shifted_load, output_path):
        shifted_load.to_csv(output_path, sep=',', index=False, header=True)

    # Main execution
    df_heating_periods = extract_q_heating_and_periods(path_to_excel_file_BAU)
    df_index = extract_index(path_to_excel_file_BAU)

    heating_data_df = merge_dataframes_and_save(df_index, df_heating_periods)

    heating_data = heating_data_df['House_Q_heating'].tolist()

    load_profile = read_and_process_csv(path_to_load_profile)

    # Optimize load profile excluding the last two hours (extreme values)
    total_SH, shifted_load_df_SH = optimize_load_profile(load_profile, heating_data, model_path_SH)

    save_load_profile(shifted_load_df_SH, output_path)

    return total_SH, shifted_load_df_SH, heating_data


# Example call
path_to_load_profile = r'C:\Users\there\Desktop\REHO2\scripts\templates\yearly_data_centre_profile_repeated2.csv'
path_to_excel_file_BAU = r'C:\\Users\\there\\Desktop\\REHO2\\scripts\\template\\results\\ALL_EPFL_BAU_gwp.xlsx'
model_path_SH = r'C:\Users\there\Desktop\REHO2\scripts\templates\switchLoad\data_heat_switch_before_clustering_use.mod'
output_path = r'C:\Users\there\Desktop\REHO2\scripts\templates\yearly_data_centre_profile_repeated4.csv'

total_SH, shifted_load_df_SH, heating_data = process_and_optimize_data_space_heating(path_to_load_profile,
                                                                                     path_to_excel_file_BAU,
                                                                                     model_path_SH, output_path)

# plotting
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
ax2.plot(heating_data[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='SH')
ax2.set_ylim(min(heating_data[:242]), max(heating_data[:242]) * 1.1)  # Add some space above the maximum value
ax2.set_ylabel('SH', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
plt.show()