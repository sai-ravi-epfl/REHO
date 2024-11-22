import pandas as pd
import os

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


def merge_dataframes_and_save(df_index, df_heating_periods, output_csv):
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

    # Save the load profile SH DataFrame to a new CSV file named 'load_profile_SH.csv'
    load_profile_sh.to_csv(output_csv, index=False)


# Example call
excel_file = r'/scripts/template/results/ALL_EPFL_BAU_gwp.xlsx'
output_csv = 'load_profile_SH.csv'

df_heating_periods = extract_q_heating_and_periods(excel_file)
df_index = extract_index(excel_file)
merge_dataframes_and_save(df_index, df_heating_periods, output_csv)