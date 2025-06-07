import numpy as np
import cvxpy as cp
import pandas as pd
import matplotlib.pyplot as plt

from reho.paths import path_to_profiles

# Load the full-year CSV profiles
file_path_irr = path_to_profiles + '/pully.csv'
df_irr_profile = pd.read_csv(file_path_irr)
irradiation = df_irr_profile['Irr'].values  # shape (8760,)

file_path_dc = path_to_profiles + '/yearly_data_centre_profile_repeated2.csv'
df_dc_load = pd.read_csv(file_path_dc)
datacentre_load = df_dc_load['Load_Profile'].values  # shape (8760,)

# Normalize both profiles to [0, 1] range
irr_norm = irradiation / np.max(irradiation)
dc_norm = datacentre_load / np.max(datacentre_load)

# Time index
T = len(dc_norm)
hours = np.arange(T)

# Optimization variables
S = cp.Variable(T)
delta_pos = cp.Variable(T)
delta_neg = cp.Variable(T)

constraints = [
    S == dc_norm - delta_neg + delta_pos,
    delta_neg <= 0.3 * dc_norm,
    cp.sum(delta_pos) == cp.sum(delta_neg),
    delta_pos >= 0,
    delta_neg >= 0,
    S >= 0,
    S[0] == dc_norm[0],  # Ensure the first point aligns
    S[-1] == dc_norm[-1]  # Ensure the last point aligns
]

# Objective: match shifted DC load to irradiation shape
objective = cp.Minimize(cp.sum_squares(S - irr_norm))
prob = cp.Problem(objective, constraints)
prob.solve()

# Plot one representative week (e.g., week 26 = hours 3120 to 3192)

# Plot one representative week (e.g., week 26 = hours 3120 to 3192)

S_plot = S.value / np.max(S.value)  # normalize shifted profile just for plotting
start = 3120
end = start + 168
plt.figure(figsize=(10, 6))
plt.plot(hours[start:end], dc_norm[start:end], label="Original Data Center Load", linestyle='-')
plt.plot(hours[start:end], S_plot[start:end], label="Shifted Data Center Load", linestyle='-')
plt.plot(hours[start:end], irr_norm[start:end], label="Irradiation", linestyle='-')
plt.xlabel("Hour of Year", fontsize=14, fontname='Arial')
plt.ylabel("Normalized Value", fontsize=14, fontname='Arial')
plt.legend(fontsize=11)

plt.xticks(fontsize=12, fontname='Arial')
plt.yticks(fontsize=12, fontname='Arial')


plt.tight_layout()
plt.ylim(bottom=0)  # Set y-axis to start at 0
plt.xlim(left=start)  # Ensure the plot starts at the first hour
plt.savefig("shifted_load_vs_irradiation.png", dpi=900)  # Save with 300 dpi for high resolution
plt.show()


# Re-scale the shifted profile (S.value) back to original kW units
S_scaled = S.value * np.max(datacentre_load)

# Create a DataFrame in the required format
df_shifted = pd.DataFrame({
    "Hour": np.arange(1, len(S_scaled) + 1),
    "Load_Profile": S_scaled
})

# Save to CSV
df_shifted.to_csv(path_to_profiles + "/shifted_datacentre_profile_sai.csv", index=False)
