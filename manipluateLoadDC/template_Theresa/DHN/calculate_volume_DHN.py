import numpy as np
import pandas as pd

# This script calculates the total volume of pipes in a District Heating Network (DHN) based on their lengths and diameters provided in a CSV file.
# The CSV file should contain the following columns:
# - 'u': Start point of the pipe (not used in calculations)
# - 'v': End point of the pipe (not used in calculations)
# - 'length': Length of the pipe in meters
# - 'diameter': Diameter of the pipe in meters
# The script reads the CSV file, calculates the volume for each pipe, and sums up the volumes to get the total volume.

# Function to calculate the volume of the pipes in the DHN
def calculate_volume_DHN(DHN_length, DHN_diameter):
    """
    Calculate the volume of the pipes in the DHN to get the thermal storage volume of the DHN

    :param DHN_length: float, length of the DHN
    :param DHN_diameter: float, diameter of the DHN
    :return: float, volume of the pipes in the DHN
    """
    # Calculate the volume of the pipes in the DHN
    DHN_volume = np.pi * (DHN_diameter / 2) ** 2 * DHN_length
    return DHN_volume

# Function to extract DHN_length and DHN_diameter from a CSV file and calculate total volume
def extract_and_calculate_total_volume(path_to_DHN_csv):
    """
    Extract DHN_length and DHN_diameter from a CSV file and calculate total volume

    :param path_to_DHN_csv: str, path to the CSV file
    :return: float, total volume of the pipes in the DHN
    """
    # Read the csv file
    df = pd.read_csv(path_to_DHN_csv)

    # Initialize total volume
    total_volume = 0

    # Iterate over each row to calculate and sum up the volumes
    for index, row in df.iterrows():
        length = row['length']
        diameter = row['diameter']
        volume = calculate_volume_DHN(length, diameter)
        total_volume += volume

    return total_volume

# Path to the CSV file
path_to_DHN_csv = 'EPFL_0_EPFL_70_60_water_02_Q_peak_1.5_gurobi_simplified_tree_diameter.csv'  # Replace with your actual CSV file path

# Calculate the total volume of the pipes in the DHN
total_volume = extract_and_calculate_total_volume(path_to_DHN_csv)
print(f"The total volume of the pipes in the DHN is {total_volume} cubic meters.")


# Calculate the volume of the pipes in the DHN
path_to_DHN_csv = 'EPFL_1_EPFL_70_60_water_02_Q_peak_1.5_gurobi_simplified_tree_diameter.csv'
# Calculate the total volume of the pipes in the DHN
total_volume = extract_and_calculate_total_volume(path_to_DHN_csv)
print(f"The total volume of the pipes in the DHN is {total_volume} cubic meters.")