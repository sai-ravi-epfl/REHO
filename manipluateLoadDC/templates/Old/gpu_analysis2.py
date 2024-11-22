import os
import pandas as pd
import matplotlib.pyplot as plt

def read_and_process_csv(file_name):
    """Reads a CSV file in chunks and processes it to return hourly averages."""
    chunk_list = []
    for chunk in pd.read_csv(file_name, chunksize=100000):
        chunk.columns = ['time_stamp', 'readable_time', 'value']
        chunk['value'] = pd.to_numeric(chunk['value'], errors='coerce', downcast='float')
        chunk.dropna(subset=['value'], inplace=True)
        chunk['hour'] = chunk['readable_time'].str[:2].astype(int)
        hourly_avg = chunk.groupby('hour')['value'].mean().to_frame(name='value')
        chunk_list.append(hourly_avg)
    return pd.concat(chunk_list)

def process_gpu_data(gpu_folder, gpu_id, date_range):
    """Processes data for a single GPU over a given date range."""
    gpu_data = []
    for date in date_range:
        file_name = os.path.join(gpu_folder, f"gpu{gpu_id:03d}_power_{date.strftime('%Y-%m-%d')}.csv")
        if os.path.exists(file_name):
            print(f"Processing file: {file_name}")  # Debug output
            hourly_avg = read_and_process_csv(file_name)
            gpu_data.append(hourly_avg)
        else:
            print(f"File not found: {file_name}")  # Debug output
    if gpu_data:
        gpu_data = pd.concat(gpu_data).reset_index()
        return gpu_data
    return None

def calculate_hourly_averages(base_path, date_range):
    """Calculates hourly averages for all GPUs."""
    hourly_averages = pd.DataFrame()
    for gpu_id in range(1, 33):
        gpu_folder = os.path.join(base_path, f"gpu{gpu_id:03d}\\power")
        print(f"Processing GPU {gpu_id:03d} in folder {gpu_folder}")  # Debug output
        hourly_avg_gpu = process_gpu_data(gpu_folder, gpu_id, date_range)
        if hourly_avg_gpu is not None:
            hourly_avg_gpu.columns = [f'gpu{gpu_id:03d}' if col == 'value' else col for col in hourly_avg_gpu.columns]
            if hourly_averages.empty:
                hourly_averages = hourly_avg_gpu
            else:
                hourly_averages = hourly_averages.add(hourly_avg_gpu.set_index('hour'), fill_value=0)
        else:
            print(f"No data for GPU {gpu_id:03d}")  # Debug output
    hourly_averages['total_power'] = hourly_averages.sum(axis=1)
    return hourly_averages

def plot_total_power(hourly_averages):
    """Plots the total power consumption over time."""
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_averages.index, hourly_averages['total_power'], linestyle='-', marker='')
    plt.xlabel('Hours')
    plt.ylabel('Total Power Consumption')
    plt.title('Total Power Consumption per Hour (April 2024 - July 2024) Watt')
    plt.grid(True)
    plt.show()

def main():
    base_path = r"C:\Users\there\Downloads\rcp_power_20240829\data_power"
    start_date = pd.to_datetime("2024-04-23")
    end_date = pd.to_datetime("2024-07-29")
    date_range = pd.date_range(start_date, end_date)

    hourly_averages = calculate_hourly_averages(base_path, date_range)
    print(hourly_averages.head())  # Debug output
    plot_total_power(hourly_averages)

if __name__ == "__main__":
    main()

