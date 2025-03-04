"""
Input:
- CSV file path: Path to the original load profile CSV file.

Functionality:
1. Reads the CSV file and processes the data.
2. Adjusts the data center size values.
3. Writes the processed data to a new CSV file.
"""

import csv

# Read the CSV file
with open(r'C:\Users\there\Desktop\REHO2\scripts\templates\original load profile\yearly_data_centre_profile_repeated2.csv', 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # Read the header
    rows = list(reader)  # Read the rest of the data

# Process the data
processed_rows = []
for row in rows:
    hour = row[0]
    load_profile = float(row[1])
    new_load_profile = (load_profile / 288) * 2000
    processed_rows.append([hour, new_load_profile])

# Write the processed data to a new CSV file
with open('data_centre_profile_2MW.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)  # Write the header
    writer.writerows(processed_rows)  # Write the processed data

print("The processed data has been saved to 'processed_data.csv'.")
