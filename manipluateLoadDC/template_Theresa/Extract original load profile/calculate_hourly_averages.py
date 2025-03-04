"""
Input:
- base_path: Base directory path containing GPU data.
- date_range: Date range for calculating hourly averages.
- gpus: Number of GPUs to process.

Functionality:
1. read_and_process_csv(file_name): Reads a CSV file, processes it, and returns hourly averages.
2. process_gpu_data(gpu_folder, gpu_id, date_range): Processes data for a single GPU over a date range.
3. calculate_hourly_averages(base_path, date_range, gpus): Calculates hourly averages for all GPUs and saves results to CSV files.
4. main(): Defines base path, date range, and number of GPUs, then starts the calculation of hourly averages.
"""

import os
import pandas as pd

def read_and_process_csv(file_name):
    """Reads a CSV file and processes it to return hourly averages."""
    df = pd.read_csv(file_name)  # Read the CSV file
    df.columns = ['time_stamp', 'readable_time', 'value']  # Rename columns
    df['value'] = pd.to_numeric(df['value'], errors='coerce', downcast='float')  # Convert 'value' to numeric type
    df.dropna(subset=['value'], inplace=True)  # Remove rows with missing 'value'
    df['hour'] = df['readable_time'].str[:2].astype(int)  # Extract hour from 'readable_time'
    hourly_avg = df.groupby('hour')['value'].mean().to_frame(name='Load_Profile')  # Calculate hourly averages
    hourly_avg.reset_index(inplace=True)  # Reset index
    hourly_avg.rename(columns={'hour': 'Hour'}, inplace=True)  # Rename 'hour' column to 'Hour'
    return hourly_avg  # Return hourly averages

def process_gpu_data(gpu_folder, gpu_id, date_range):
    """Processes data for a single GPU over a given date range."""
    gpu_data = []
    for date in date_range:
        file_name = os.path.join(gpu_folder, f"gpu{gpu_id:03d}_power_{date.strftime('%Y-%m-%d')}.csv")  # Create file name
        if os.path.exists(file_name):
            print(f"Processing file: {file_name}")  # Debug output
            hourly_avg = read_and_process_csv(file_name)  # Read and process CSV file
            gpu_data.append(hourly_avg)  # Append processed data
        else:
            print(f"File not found: {file_name}")  # Debug output
    if gpu_data:
        gpu_data = pd.concat(gpu_data).reset_index(drop=True)  # Concatenate all data and reset index
        return gpu_data  # Return concatenated data
    return None  # No data found

def calculate_hourly_averages(base_path, date_range, gpus):
    """Calculates hourly averages for all GPUs."""
    for gpu_id in range(1, gpus+1):
        gpu_folder = os.path.join(base_path, f"gpu{gpu_id:03d}\\power")  # Create GPU folder path
        print(f"Processing GPU {gpu_id:03d} in folder {gpu_folder}")  # Debug output
        hourly_avg_gpu = process_gpu_data(gpu_folder, gpu_id, date_range)  # Process data for GPU
        if hourly_avg_gpu is not None:
            hourly_avg_gpu.to_csv(f'hourly_averages_gpu{gpu_id:03d}.csv', index=False)  # Save results to CSV file
            print(f"Hourly averages for GPU {gpu_id:03d} saved to hourly_averages_gpu{gpu_id:03d}.csv")  # Debug output
        else:
            print(f"No data for GPU {gpu_id:03d}")  # Debug output

def main():
    base_path = r"C:\Users\there\Documents\Uni\Msc_MechanicalEngineering\rcp_power_20240829\data_power"  # Base directory, change accordingly to where stored

    # start_date and end_date are the date range for which to calculate hourly averages
    start_date = pd.to_datetime("2024-04-23")
    end_date = pd.to_datetime("2024-07-29")
    gpus = 32  # Number of GPUs
    date_range = pd.date_range(start_date, end_date)  # Create date range

    calculate_hourly_averages(base_path, date_range, gpus)  # Calculate hourly averages

if __name__ == "__main__":
    main()  # Execute main function