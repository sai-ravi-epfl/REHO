import pandas as pd
import amplpy
import matplotlib.pyplot as plt


# load GWP100a profile from electricity_matrix_2019_reduced.csv in a dataframe with the index 'Hour'
path_to_emissions = r'/reho/data/emissions/electricity_matrix_2019_reduced.csv'
emissions_matrix = pd.read_csv(path_to_emissions, index_col=[0, 1, 2])
# get values where CH and GWP20a
gwp_row = emissions_matrix.loc[(emissions_matrix.index.get_level_values(2) == 'GWP100a') & (emissions_matrix.index.get_level_values(0) == 'CH')]
# change row to column
gwp_profile = gwp_row.T
# delete first two rows and set index to 'Hour' starting from 1
gwp_profile.index = range(1, len(gwp_profile) + 1)
gwp_profile.index.name = 'Hour'
gwp_profile.columns = ['gwp']
# save GWP100a profile in a csv file
gwp_profile.to_csv('gwp_profile_grid.csv')


# load csv file
load_profile = pd.read_csv('../yearly_data_centre_profile_repeated2.csv')
gwp_profile = pd.read_csv('../switchLoad/gwp_profile_grid.csv')

# save data in AMPL compatible format (dat)
with open('data_switch_GWP.dat', 'w') as f:
    f.write('param load :=\n')
    for i, load in enumerate(load_profile['Load_Profile']):
        f.write(f'{i + 1} {load}\n')
    f.write(';\n')

    f.write('param gwp :=\n')
    for i, gwp in enumerate(gwp_profile['gwp']):
        f.write(f'{i + 1} {gwp}\n')
    f.write(';\n')

# AMPL
ampl = amplpy.AMPL()
ampl.setOption('solver', 'gurobi')

# load model and data
ampl.read('data_heat_switch.mod')
ampl.readData('data_switch_GWP.dat')

# run optimisation
ampl.solve()

# show results
shifted_load = ampl.getVariable('shifted_load').getValues()
total_gwp = ampl.getObjective('total_gwp').value()

# Convert shifted_load to a pandas DataFrame
shifted_load_df = shifted_load.toPandas()
shifted_load_df.index.name = 'Hour'
shifted_load_df.columns = ['Load_Profile']
shifted_load_df.reset_index(inplace=True)


# Save the DataFrame to a CSV file
shifted_load_df.to_csv('shifted_load_GWP_before_clustering.csv', index=False)

### plotting
'''
plt.figure(figsize=(12, 6))
plt.plot(shifted_load_df['Hour'], shifted_load_df['Load_Profile'], linestyle='-', marker='', color='b', linewidth=1.5)
plt.xlabel('Hours', fontsize=14)
plt.ylabel('Shifted Load [kW]', fontsize=14)
plt.title('Shifted Load per Hour', fontsize=16)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
filename = 'shifted_load.png'
plt.savefig(filename, dpi=300)  # Save the plot as a high-quality image
plt.show()


# plot just first 72 hours of not smoothed data
plt.plot(shifted_load_df['Hour'][:72], shifted_load_df['Load_Profile'][:72], linestyle='-', marker='', color='b', linewidth=1.5)
plt.xlabel('Hours', fontsize=14)
plt.ylabel('Load [kW]', fontsize=14)
plt.title('Load per Hour', fontsize=16)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
filename = 'shifted_load_day.png'
plt.savefig(filename, dpi=300)  # Save the plot as a high-quality image
plt.show()


# plot just first 72 hours of not smoothed data and put in same plot original data for first 72 hours
plt.plot(shifted_load_df['Hour'][:168], shifted_load_df['Load_Profile'][:168], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
plt.plot(load_profile['Load_Profile'][:168], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
plt.xlabel('Hours', fontsize=14)
plt.ylabel('Load [kW]', fontsize=14)
plt.title('Load per Hour', fontsize=16)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend()
filename = 'shifted_load_week_comparison_GWP_grid_vs_orginal.png'
plt.savefig(filename, dpi=300)  # Save the plot as a high-quality image
plt.show()


# do the same but add a second axis with GWP profile
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot original and shifted load on primary y-axis
ax1.plot(shifted_load_df['Hour'][:168], shifted_load_df['Load_Profile'][:168], linestyle='-', marker='', color='b', linewidth=1.5, label='Shifted Load')
ax1.plot(load_profile['Load_Profile'][:168], linestyle='-', marker='', color='r', linewidth=1.5, label='Original Load')
ax1.set_xlabel('Hours', fontsize=14)
ax1.set_ylabel('Load [kW]', fontsize=14, color='black')
ax1.tick_params(axis='y', labelcolor='black')

# Create a secondary y-axis for GWP
ax2 = ax1.twinx()
ax2.plot(gwp_profile['gwp'][:168], linestyle='-', marker='', color='g', linewidth=1.5, label='GWP')
ax2.set_ylabel('GWP', fontsize=14, color='black')
ax2.tick_params(axis='y', labelcolor='black')

# Title and grid
ax1.set_title('Load per Hour', fontsize=16)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax1.tick_params(axis='x', labelsize=12)
ax1.tick_params(axis='y', labelsize=12)
ax2.tick_params(axis='y', labelsize=12)

# Add legend
fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

# Save and show the plot
filename = 'shifted_load_week_comparison_GWP_grid_vs_original.png'
fig.savefig(filename, dpi=300)  # Save the plot as a high-quality image
plt.show()
'''