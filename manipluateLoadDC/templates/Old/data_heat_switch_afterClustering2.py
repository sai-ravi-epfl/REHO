import pandas as pd
import amplpy
import matplotlib.pyplot as plt
import csv
from datetime import datetime

# write function to read and process csv file
def read_and_process_csv(file_name):
    # load load profile of data centre after clustering
    # TO do: find way that automatically analyse which cluster is used and access right file)
    path_to_load_profile = r'/scripts/template/data/clustering/D_Pully_10_24_T_I_W_D.dat'
    # read csv files
    load_profile = pd.read_csv(path_to_load_profile, sep='\t', header=None)

    # load GWP100a profile from electricity_matrix_2019_reduced.csv in a dataframe with the index 'Hour'
    path_to_emissions = r'/reho/data/emissions/electricity_matrix_2019_reduced.csv'
    emissions_matrix = pd.read_csv(path_to_emissions, index_col=[0, 1, 2])
    # get values where CH and GWP100a
    gwp_row = emissions_matrix.loc[(emissions_matrix.index.get_level_values(2) == 'GWP100a') & (emissions_matrix.index.get_level_values(0) == 'CH')]
    # change row to column
    gwp_profile = gwp_row.T
    # delete first two rows and set index to 'Hour' starting from 1
    gwp_profile.index = range(1, len(gwp_profile) + 1)
    gwp_profile.index.name = 'Hour'
    gwp_profile.columns = ['gwp']
    # save GWP100a profile in a csv file
    gwp_profile.to_csv('gwp_profile_grid.csv')

    return load_profile, gwp_profile

# 1. Step: find timestamp.dat file and convert it to a pandas dataframe
path_to_timestamp = r'/scripts/template/data/clustering/timestamp_Pully_10_24_T_I_W_D.dat'
# convert timestamp.dat file to a pandas dataframe
df_Timestamp = pd.read_csv(path_to_timestamp, sep='\t', header=None)
# save as csv file
df_Timestamp.to_csv('timestamp.csv')

input_file_path = r'/scripts/template/data/clustering/timestamp_Pully_10_24_T_I_W_D.dat'
output_file_path = '../switchLoad/timestamp_with_hour_of_year.csv'
hourly_gwp_profile_path = '../switchLoad/gwp_profile_grid.csv'


def calculate_hour_of_year(timestamp):
    dt = datetime.strptime(timestamp, '%m/%d/%Y/%H')
    new_year_day = datetime(dt.year, 1, 1)
    hour_of_year = int((dt - new_year_day).total_seconds() // 3600)
    return hour_of_year

# read .dat file and write .csv file with adding columns for hour of the year to the timestamp
with open(input_file_path, 'r') as dat_file, open(output_file_path, 'w', newline='') as csv_file:
    reader = csv.reader(dat_file, delimiter='\t')
    writer = csv.writer(csv_file, delimiter=',')

    # write header with anther columns for hour of year
    header = next(reader)
    header.append('HourOfYear')
    writer.writerow(header)

    for row in reader:
        timestamp = row[0]
        hour_of_year = calculate_hour_of_year(timestamp)
        row.append(hour_of_year)
        writer.writerow(row)

# 2. Step: find same days as timestamp in gwp profile of grid and extract them in same format as load profile
days = []
extreme_hours = []
with open(output_file_path, 'r') as timestamp_file:
    reader = csv.DictReader(timestamp_file)
    for row in reader:
        days.append(int(row['Day']))
        extreme_hours.append(int(row['HourOfYear']))

filtered_values = []
extreme_values = []
with open(hourly_gwp_profile_path, 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)
    for row in reader:
        hour = int(row[0])
        gwp = float(row[1])
        day_of_year = (hour - 1) // 24 + 1
        if day_of_year in days[:-2]:  # all days except last two
            filtered_values.append(gwp)
        if day_of_year == days[-2] or day_of_year == days[-1]:  # only last two
            if hour == calculate_hour_of_year('07/20/2005/00') or hour == calculate_hour_of_year('07/11/2005/00'):
                extreme_values.append(gwp)

# 3. Step: save both profiles in a csv file
with open(output_file_path, 'w') as dat_file:
    for value in filtered_values:
        dat_file.write(f"{value}\n")
    for value in extreme_values:
        dat_file.write(f"{value}\n")


# 4. Step: save both profiles in a dat file
# 5. Step: run optimisation
# 6. Step: show results
# 7. Step: plot results





