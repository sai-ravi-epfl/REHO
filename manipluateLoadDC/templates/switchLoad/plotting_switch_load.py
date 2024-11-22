import pandas as pd
import matplotlib.pyplot as plt

def get_and_extract_performance(excel_file):
    sheet_name = 'df_Performance'
    columns = ['Costs_inv', 'Costs_rep', 'Costs_op', 'Costs_grid_connection', 'GWP_op', 'GWP_constr']

    # Load the Excel file
    df_performance = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=columns)

    # Calculate CAPEX, OPEX, TOTEX, and GWP
    df_performance['CAPEX'] = df_performance['Costs_inv'] + df_performance['Costs_rep']
    df_performance['OPEX'] = df_performance['Costs_op'] + df_performance['Costs_grid_connection']
    df_performance['TOTEX'] = df_performance['CAPEX'] + df_performance['OPEX']
    df_performance['GWP'] = df_performance['GWP_op'] + df_performance['GWP_constr']

    return df_performance[['CAPEX', 'OPEX', 'TOTEX', 'GWP']]

# Load the Excel files
file_path_ORC_50kW = r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_ORC_50kW_DC_gwp.xlsx'
file_path_ORC_50kW_switch_gwp = r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_ORC_switch_gwp_50kW_DC_gwp.xlsx'
file_path_ORC_50kW_switch_SH = r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_ORC_switch_SH_50kW_DC_gwp.xlsx'
file_path_ORC_50kW_switch_ED = r'C:\Users\there\Desktop\REHO2\scripts\template\results\ALL_EPFL_ORC_switch_ED_50kW_DC_gwp.xlsx'

# Extract the performance data
df_ORC_50kW = get_and_extract_performance(file_path_ORC_50kW)
df_ORC_50kW_switch_gwp = get_and_extract_performance(file_path_ORC_50kW_switch_gwp)
df_ORC_50kW_switch_SH = get_and_extract_performance(file_path_ORC_50kW_switch_SH)
df_ORC_50kW_switch_ED = get_and_extract_performance(file_path_ORC_50kW_switch_ED)

# Combine the data into a single DataFrame for plotting
df_combined = pd.DataFrame({
    'Scenario': ['ORC 50kW', 'ORC 50kW switch GWP', 'ORC 50kW switch SH', 'ORC 50kW switch ED'],
    'CAPEX': [df_ORC_50kW['CAPEX'].sum(), df_ORC_50kW_switch_gwp['CAPEX'].sum(), df_ORC_50kW_switch_SH['CAPEX'].sum(), df_ORC_50kW_switch_ED['CAPEX'].sum()],
    'OPEX': [df_ORC_50kW['OPEX'].sum(), df_ORC_50kW_switch_gwp['OPEX'].sum(), df_ORC_50kW_switch_SH['OPEX'].sum(), df_ORC_50kW_switch_ED['OPEX'].sum()],
    'TOTEX': [df_ORC_50kW['TOTEX'].sum(), df_ORC_50kW_switch_gwp['TOTEX'].sum(), df_ORC_50kW_switch_SH['TOTEX'].sum(), df_ORC_50kW_switch_ED['TOTEX'].sum()],
    'GWP': [df_ORC_50kW['GWP'].sum(), df_ORC_50kW_switch_gwp['GWP'].sum(), df_ORC_50kW_switch_SH['GWP'].sum(), df_ORC_50kW_switch_ED['GWP'].sum()]
})

# Plot the costs (CAPEX, OPEX, TOTEX)
fig, ax1 = plt.subplots(figsize=(12, 8))
bar_width = 0.2
bar_spacing = 0.05
index = range(len(df_combined))

# Plot the costs on the left axis
ax1.bar([i - bar_width - bar_spacing for i in index], df_combined['CAPEX'], bar_width, label='CAPEX')
ax1.bar(index, df_combined['OPEX'], bar_width, label='OPEX')
ax1.bar([i + bar_width + bar_spacing for i in index], df_combined['TOTEX'], bar_width, label='TOTEX')
ax1.set_xlabel('Scenario')
ax1.set_ylabel('Costs [CHF]')
ax1.tick_params(axis='y')
ax1.legend(loc='upper left')

# Add grid lines to indicate differences
ax1.yaxis.grid(True)

# Set the x-axis labels
ax1.set_xticks(index)
ax1.set_xticklabels(df_combined['Scenario'])

# Set the title and display the plot
plt.title('Comparison of CAPEX, OPEX, and TOTEX for Different Scenarios')
plt.tight_layout()

# Save the plot as an image file
plt.savefig('costs_comparison.png')

plt.show()

# Plot the GWP
fig, ax2 = plt.subplots(figsize=(12, 8))
bar_width = 0.2

# Plot the GWP on the left axis
ax2.bar(index, df_combined['GWP'], bar_width, label='GWP', color='tab:orange')
ax2.set_xlabel('Scenario')
ax2.set_ylabel('GWP [kg CO2-eq]')
ax2.tick_params(axis='y')
ax2.legend(loc='upper left')

# Add grid lines to indicate differences
ax2.yaxis.grid(True)

# Set the x-axis labels
ax2.set_xticks(index)
ax2.set_xticklabels(df_combined['Scenario'])

# Set the title and display the plot
plt.title('Comparison of GWP for Different Scenarios')
plt.tight_layout()

# Save the plot as an image file
plt.savefig('gwp_comparison.png')

plt.show()
