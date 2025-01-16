import pandas as pd
import amplpy
import matplotlib.pyplot as plt
import numpy as np

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

    return total_use, shifted_load, profile_data_df#