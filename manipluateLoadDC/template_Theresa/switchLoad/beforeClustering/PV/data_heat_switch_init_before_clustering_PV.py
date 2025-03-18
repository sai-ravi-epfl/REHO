import pandas as pd
import amplpy
import matplotlib.pyplot as plt

def process_and_optimize_data_PV(path_to_load_profile, path_to_PV, model_path, output_path, size=288):
    def read_and_process_dat(path_to_load_profile, path_to_PV):
        # Load the profile of the data center before clustering from a CSV file
        load_profile = pd.read_csv(path_to_load_profile)
        load_profile = load_profile['Load_Profile'].values  # Extract the Load_Profile column as a numpy array

        # Load PV supply data
        PV_profile = pd.read_csv(path_to_PV, sep=',', header=None, skiprows=1)  # Skip the first row
        PV_profile.columns = ['Hour', 'PV_supply']
        PV_profile.set_index('Hour', inplace=True)
        return load_profile, PV_profile

    def optimize_load_profile(load_profile, filtered_PV_profile, model_path, size=288):
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.read(model_path)
        ampl.eval(f'let size := {size};')
        T = 8760  # Number of hours in a year

        # Prepare data for AMPL
        load_data = {i + 1: load for i, load in enumerate(load_profile[:T])}
        PV_data = {i + 1: (float(gwp) if pd.notna(gwp) else 0) for i, gwp in enumerate(filtered_PV_profile['PV_supply'][:T])}

        # Debug: Print the contents of PV_data
       # print("PV_data:", PV_data)

        # Set data in AMPL
        ampl.param['load'] = load_data
        ampl.param['objective'] = PV_data

        # Solve the optimization problem
        ampl.solve()

        # Retrieve the optimized load profile
        shifted_load = ampl.getVariable('shifted_load').getValues().toPandas()
        shifted_load.index.name = 'Hour'
        shifted_load.columns = ['Load_Profile']
        shifted_load.reset_index(inplace=True)

        # Get the total PV supply used
        total_PV = ampl.getObjective('use').value()
        return total_PV, shifted_load

    def save_load_profile(shifted_load, output_path):
        # Save the optimized load profile to a CSV file
        shifted_load.to_csv(output_path, sep=',', index=False, header=True)

    # Read and process the input data
    load_profile, PV_profile = read_and_process_dat(path_to_load_profile, path_to_PV)

    # Optimize the load profile using the PV supply data
    total_PV_supply, shifted_load_df_PV = optimize_load_profile(load_profile, PV_profile, model_path, size)

    # Save the optimized load profile
    save_load_profile(shifted_load_df_PV, output_path)

    return total_PV_supply, shifted_load_df_PV, PV_profile

# Example call for PV
path_to_load_profile = r'C:\Users\there\Desktop\REHO2\manipluateLoadDC\template_Theresa\yearly_data_centre_profile_repeated2.csv'
path_to_PV = r'reconstructed_year_16clusters_new.csv'
model_path = r'C:\Users\there\Desktop\REHO2\manipluateLoadDC\template_Theresa\switchLoad\beforeClustering\data_heat_switch_before_clustering_use.mod'
size = 288
output_path = r'C:\Users\there\Desktop\REHO2\manipluateLoadDC\template_Theresa\switchLoad\beforeClustering\PV\yearly_data_centre_profile_PV_16clusters_TIED_24h_new.csv'

total_PV, shifted_load_df_PV, PV_profile = process_and_optimize_data_PV(path_to_load_profile, path_to_PV, model_path, output_path, size)

'''
# Plotting for GWP
load_profile = pd.read_csv(path_to_load_profile)
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_PV['Hour'][:168], shifted_load_df_PV['Load_Profile'][:168], linestyle='-', marker='',
         color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:168], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hour of the year', fontsize=14)
ax1.set_ylabel('Load DC [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(0, 168)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(PV_profile[:168], linestyle='-', marker='', color='g', linewidth=1.5, label='PV supply')
ax2.set_ylim(bottom=0)
ax2.set_ylabel('PV [kW]', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
filename = 'shifted_load_week_comparison_PV_supply_vs_original.png'
plt.show()
fig.savefig(filename, dpi=300)
'''