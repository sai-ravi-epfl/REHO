import pandas as pd
import matplotlib.pyplot as plt

# Load and sum hourly averages for all GPUs
def load_and_sum_hourly_averages(gpus):
    """Loads hourly averages for all GPUs and sums them."""
    hourly_averages = pd.DataFrame()
    for gpu_id in range(1, gpus+1):
        file_name = f'hourly_averages_gpu{gpu_id:03d}.csv'
        gpu_data = pd.read_csv(file_name)
        if hourly_averages.empty:
            hourly_averages = gpu_data
        else:
            hourly_averages = hourly_averages.add(gpu_data, fill_value=0)
    hourly_averages['Load_Profile'] = hourly_averages.sum(axis=1)
    hourly_averages.rename(columns={'Hour': 'Hour'}, inplace=True)
    # Convert to kW
    hourly_averages['Load_Profile'] = hourly_averages['Load_Profile'] / 1000
    return hourly_averages

def plot_total_power(hourly_averages, filename='data_centre_profile.png'):
    """Plots the total power consumption over time and saves it as a high-quality image."""
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_averages.index, hourly_averages['Load_Profile'], linestyle='-', marker='')
    plt.xlabel('Hours')
    plt.ylabel('Total Power Consumption [kW]')  # Convert to kW for this plot
    plt.title('Total Power Consumption per Hour')
    plt.grid(True)
    plt.savefig(filename, dpi=300)  # Save the plot as a high-quality image
    plt.show()

def save_total_power_to_csv(hourly_averages, filename='data_centre_profile.csv'):
    """Saves the total power consumption per hour to a CSV file."""
    hourly_averages['Hour'] = hourly_averages.index + 1  # Ensure correct hourly labels
    hourly_averages[['Hour', 'Load_Profile']].to_csv(filename, index=False)

def repeat_data_to_one_year(hourly_averages):
    """Repeats the data until there are 8760 hours (one year)."""
    num_hours = len(hourly_averages)
    repeat_times = (8760 // num_hours) + 1
    repeated_data = pd.concat([hourly_averages] * repeat_times, ignore_index=True)
    repeated_data = repeated_data.iloc[:8760]
    repeated_data['Hour'] = repeated_data.index + 1  # Ensure correct hourly labels from 1 to 8760
    # Ensure Load_Profile is in kW
    repeated_data['Load_Profile'] = repeated_data['Load_Profile']
    return repeated_data

def plot_yearly_data(hourly_averages, filename='yearly_data_centre_profile_repeated2.png'):
    """Plots the total power consumption over time and saves it as a high-quality image."""
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_averages['Hour'], hourly_averages['Load_Profile'], linestyle='-', marker='')
    #start x-axis from 0
    plt.xlim(0, 8760)
    plt.xlabel('Hour of the year')
    plt.ylabel('Total Power Consumption [kW]')
    plt.grid(True)
    plt.savefig(filename, dpi=300)  # Save the plot as a high-quality image
    plt.show()

def save_yearly_data_to_csv(hourly_averages, filename='yearly_data_centre_profile_repeated2.csv'):
    """Saves the total power consumption per hour to a CSV file."""
    hourly_averages[['Hour', 'Load_Profile']].to_csv(filename, index=False)

def main():
    gpus = 32 # gpus is the number of gpus
    hourly_averages = load_and_sum_hourly_averages(gpus)

    # Plot and save the original data
    plot_total_power(hourly_averages, 'data_centre_profile.png')
    save_total_power_to_csv(hourly_averages, 'data_centre_profile.csv')

    # Repeat data to one year
    yearly_data = repeat_data_to_one_year(hourly_averages)

    # Plot and save the repeated data
    yearly_plot_fig = plot_yearly_data(yearly_data, 'yearly_data_centre_profile_repeated2.png')
    #save as high quality image
    yearly_plot_fig.savefig('yearly_data_centre_profile_repeated2.png', dpi=300)

    save_yearly_data_to_csv(yearly_data, '../yearly_data_centre_profile_repeated2.csv')

if __name__ == "__main__":
    main()

