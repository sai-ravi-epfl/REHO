import os
import pandas as pd


def read_and_process_csv(file_name):
    """Reads a CSV file and processes it to return hourly averages."""
    df = pd.read_csv(file_name)
    df.columns = ['time_stamp', 'readable_time', 'value']
    df['value'] = pd.to_numeric(df['value'], errors='coerce', downcast='float')
    df.dropna(subset=['value'], inplace=True)
    df['hour'] = df['readable_time'].str[:2].astype(int)
    hourly_avg = df.groupby('hour')['value'].mean().to_frame(name='Load_Profile')
    hourly_avg.reset_index(inplace=True)
    hourly_avg.rename(columns={'hour': 'Hour'}, inplace=True)
    return hourly_avg

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
        gpu_data = pd.concat(gpu_data).reset_index(drop=True)
        return gpu_data
    return None

def calculate_hourly_averages(base_path, date_range, gpus):
    """Calculates hourly averages for all GPUs."""
    for gpu_id in range(1, gpus+1):
        gpu_folder = os.path.join(base_path, f"gpu{gpu_id:03d}\\power")
        print(f"Processing GPU {gpu_id:03d} in folder {gpu_folder}")  # Debug output
        hourly_avg_gpu = process_gpu_data(gpu_folder, gpu_id, date_range)
        if hourly_avg_gpu is not None:
            hourly_avg_gpu.to_csv(f'hourly_averages_gpu{gpu_id:03d}.csv', index=False)
            print(f"Hourly averages for GPU {gpu_id:03d} saved to hourly_averages_gpu{gpu_id:03d}.csv")
        else:
            print(f"No data for GPU {gpu_id:03d}")  # Debug output

def main():
    base_path = r"C:\Users\there\Documents\Uni\MechanicalEngineering\rcp_power_20240829\data_power"

    # start_date and end_date are the date range for which to calculate hourly averages
    start_date = pd.to_datetime("2024-04-23")
    end_date = pd.to_datetime("2024-07-29")
    gpus = 32 # gpus is the number of gpus
    date_range = pd.date_range(start_date, end_date)

    calculate_hourly_averages(base_path, date_range, gpus) # hourly_average input watt and output watt

if __name__ == "__main__":
    main()