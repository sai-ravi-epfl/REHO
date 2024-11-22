import pandas as pd
import csv
from datetime import datetime
import amplpy
import numpy as np
import matplotlib.pyplot as plt


def process_and_optimize_data_GWP(path_to_load_profile, path_to_emissions, model_path, output_path, size=288):
    def read_and_process_dat(path_to_load_profile, path_to_emissions):
        # Load profile of data centre before clustering which is as csv file
        load_profile = pd.read_csv(path_to_load_profile)
        load_profile = load_profile['Load_Profile'].values  # Extract the Load_Profile column as a numpy array


        # Load GWP100a profile from electricity_matrix_2019_reduced.csv
        emissions_matrix = pd.read_csv(path_to_emissions, index_col=[0, 1, 2])
        gwp_row = emissions_matrix.loc[(emissions_matrix.index.get_level_values(2) == 'GWP100a') & (emissions_matrix.index.get_level_values(0) == 'CH')]
        gwp_profile = gwp_row.T
        gwp_profile.index = range(1, len(gwp_profile) + 1)
        gwp_profile.index.name = 'Hour'
        gwp_profile.columns = ['gwp']
        return load_profile, gwp_profile


    def optimize_load_profile(load_profile, filtered_gwp_profile, model_path, size=288):
        ampl = amplpy.AMPL()
        ampl.setOption('solver', 'gurobi')
        ampl.read(model_path)
        ampl.eval(f'let size := {size};')
        T = 8760

        load_data = {i + 1: load for i, load in enumerate(load_profile[:T])}
        gwp_data = {i + 1: gwp for i, gwp in enumerate(filtered_gwp_profile['gwp'][:T])}

        # Set data in AMPL
        ampl.param['load'] = load_data
        ampl.param['objective'] = gwp_data

        ampl.solve()

        shifted_load = ampl.getVariable('shifted_load').getValues().toPandas()
        shifted_load.index.name = 'Hour'
        shifted_load.columns = ['Load_Profile']
        shifted_load.reset_index(inplace=True)

        total_gwp = ampl.getObjective('gwp').value()
        return total_gwp, shifted_load

    def save_load_profile(shifted_load, output_path):
        shifted_load.to_csv(output_path, sep=',', index=False, header=True)

    load_profile, gwp_profile = read_and_process_dat(path_to_load_profile, path_to_emissions)

    total_gwp, shifted_load_df_GWP = optimize_load_profile(load_profile, gwp_profile, model_path)

    save_load_profile(shifted_load_df_GWP, output_path)

    return total_gwp, shifted_load_df_GWP, gwp_profile


# call function
path_to_data_centre_heat_profile = r'C:\Users\there\Desktop\REHO2\scripts\templates\yearly_data_centre_profile_repeated2.csv'
path_to_emissions = r'C:\Users\there\Desktop\REHO2\reho\data\emissions\electricity_matrix_2019_reduced.csv'
model_path = r'C:\Users\there\Desktop\REHO2\scripts\templates\switchLoad\data_heat_switch_before_clustering_gwp.mod'
size = 288
output_path = r'C:\Users\there\Desktop\REHO2\scripts\templates\yearly_data_centre_profile_repeated3.csv'

total_gwp, shifted_load_df_GWP, gwp_profile = process_and_optimize_data_GWP(path_to_data_centre_heat_profile, path_to_emissions, model_path, output_path, size)

### plotting
load_profile = pd.read_csv(path_to_data_centre_heat_profile)
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(shifted_load_df_GWP['Hour'][:242], shifted_load_df_GWP['Load_Profile'][:242], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:242], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylim(bottom=0)
ax1.set_xlim(0, 242)
ax1.xaxis.set_major_locator(plt.MultipleLocator(24))
ax2 = ax1.twinx()
ax2.plot(gwp_profile[:242], linestyle='-', marker='', color='g', linewidth=1.5, label='GWP')
ax2.set_ylim(bottom=0)
ax2.set_ylabel('GWP', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
filename = 'shifted_load_week_comparison_GWP_grid_vs_original.png'
plt.show()