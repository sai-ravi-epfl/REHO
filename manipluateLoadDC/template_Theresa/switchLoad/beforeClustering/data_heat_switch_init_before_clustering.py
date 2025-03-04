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
