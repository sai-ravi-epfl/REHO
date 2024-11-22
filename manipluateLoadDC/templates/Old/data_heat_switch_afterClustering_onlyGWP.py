import pandas as pd
import csv
from datetime import datetime


def read_and_process_csv(path_to_load_profile, path_to_emissions):
    # Load profile of data centre after clustering
    load_profile = pd.read_csv(path_to_load_profile, sep='\t', header=None, engine='python')

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


def convert_timestamp_to_csv(path_input_file, path_output_file):
    with open(path_input_file, 'r') as dat_file, open(path_output_file, 'w', newline='') as csv_file:
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

def filter_gwp_profile(path_timestamp_output, path_hourly_gwp_profile, path_filtered_output):
    days = []
    extreme_hours = []

    with open(path_timestamp_output, 'r') as timestamp_file:
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
    with open(path_filtered_output, 'w') as dat_file:
        for day in days[:-2]:
            for value in filtered_values:
                if value[0] == day:
                    dat_file.write(f"{value[1]}\n")
        for value in extreme_values:
            dat_file.write(f"{value}\n")


# Main execution
path_to_load_profile = r'/scripts/templates/data/clustering/D_Pully_10_24_T_I_E_D.dat'
path_to_emissions = r'/reho/data/emissions/electricity_matrix_2019_reduced.csv'
load_profile, gwp_profile = read_and_process_csv(path_to_load_profile, path_to_emissions)

path_timestamp_input = r'/scripts/template/data/clustering/timestamp_Pully_10_24_T_I_E_D.dat'
path_timestamp_output = '../switchLoad/timestamp_with_hour_of_year.csv'
convert_timestamp_to_csv(path_timestamp_input, path_timestamp_output)

path_hourly_gwp_profile = '../switchLoad/gwp_profile_grid.csv'
path_filtered_output = 'filtered_data.dat'
filter_gwp_profile(path_timestamp_output, path_hourly_gwp_profile, path_filtered_output)



# 5. Step: run optimisation for the filtered data except the extrem values

# 6. Step: show results
# 7. Step: plot results
