import pickle
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
import matplotlib as mpl

# Set Arial globally
mpl.rcParams['font.family'] = 'Arial'

def print_important_params(path, scenario):
    with open(path, 'rb') as f:
        data = pickle.load(f)

    print(f"\n{scenario}\n")
    results = []

    for i in data['gwp'].keys():
        unit_data = data['gwp'][i]['df_Unit']
        annuals = data['gwp'][i]['df_Annuals']

        PV_cap = unit_data[unit_data.index.str.contains('PV')]['Units_Mult'].sum()
        PV_district_total = annuals.xs('Electricity').xs('PV_district')['Supply_MWh']
        PV_buildings_total = sum(annuals.xs('Electricity').xs(f'PV_Building{l}')['Supply_MWh'] for l in range(1, 1))
        PV_produced = PV_district_total + PV_buildings_total
        DC_elec_consumption = annuals.xs('Electricity').xs('DataCentre_EPFL_district')['Demand_MWh']
        Battery_dis_cap = unit_data.xs('Battery_district').Units_Mult
        Data_cap = unit_data.xs('DataCentre_EPFL_district').Units_Mult

        network_import = annuals.xs('Electricity').xs('Network')['Supply_MWh']
        network_export = annuals.xs('Electricity').xs('Network')['Demand_MWh']
        data_import = annuals.xs('Data').xs('Network')['Supply_MWh']
        battery_in = annuals.xs('Electricity').xs('Battery_district')['Supply_MWh']
        data_in_house = annuals.xs('Data').xs('DataCentre_EPFL_district')['Supply_MWh']

        results.append({
            "Pareto ID": i,
            "PV capacity": PV_cap,
            "PV produced": PV_produced,
            "DC electricity consumption": DC_elec_consumption,
            "Battery district capacity": Battery_dis_cap,
            "Battery district charge in": battery_in,
            "Network Import": network_import,
            "Network export": network_export,
            "data in house": data_in_house,
            "Data - cloud processed": data_import,
            "Data centre size": Data_cap
        })

    df_results = pd.DataFrame(results).sort_values(by='Data centre size')
    df_results.to_csv(f"pareto_results_{scenario.replace(' ', '_')}.csv", index=False)
    return df_results

def calculate_self_metrics(df):
    df['Self sufficiency'] = (df['data in house'] / (df['data in house'] + df['Data - cloud processed'])) * 100
    df['Self consumption'] = ((df['PV produced'] - df['Network export']) / df['PV produced']) * 100
    df['Efficiency'] = ((df['PV capacity'] * df['Self consumption']) / df['Data centre size']) / 100
    return df

def plot_grouped_bar_with_secondary_star_axis(df, label, filename):
    df = df.copy()
    df['Data centre size'] = df['Data centre size'] / 1000
    df['PV capacity'] = df['PV capacity'] / 1000
    df = df.sort_values(by='Self sufficiency')

    df['Self sufficiency'] = df['Self sufficiency'].apply(
        lambda x: int(round(x / 5.0) * 5) if x >= 5 else int(round(x))
    )

    df['PV err'] = df['PV capacity'] * 0.05
    df['DC err'] = df['Data centre size'] * 0.05

    sns.set(style='white', context='talk')
    fig, ax1 = plt.subplots(figsize=(12, 9))
    ax2 = ax1.twinx()

    x = np.arange(len(df))
    width = 0.35

    ax1.bar(x - width / 2, df['PV capacity'], width=width,
            yerr=df['PV err'], capsize=5, label='PV',
            color='#1f77b4', edgecolor='black')

    ax1.bar(x + width / 2, df['Data centre size'], width=width,
            yerr=df['DC err'], capsize=5, label='Datacentre',
            color='#5f9e8f', edgecolor='black')

    ax2.plot(x, df['Self consumption'], '*', color='#e74c4c', markersize=16)

    ax1.set_xlabel("Self-sufficiency of data [%]", fontsize=26)
    ax1.set_ylabel("Capacity [MW]", fontsize=26)
    ax2.set_ylabel("Self consumption of PV [%]", color='#e74c4c', fontsize=26)

    ax1.set_xticks(x)
    ax1.set_xticklabels(df['Self sufficiency'], fontsize=26)
    ax1.tick_params(axis='x', labelsize=26)
    ax1.tick_params(axis='y', labelsize=26)
    ax2.tick_params(axis='y', colors='#e74c4c', labelsize=26)

    ax1.set_ylim(0, max(df['PV capacity'].max(), df['Data centre size'].max()) * 1.1)
    ax1.yaxis.get_major_locator().set_params(integer=True)

    ax2.set_ylim(0, 110)

    ax1.text(0.5, 0.94, label, fontsize=30, transform=ax1.transAxes, ha='center')

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def combine_plots_with_legend(filenames, output_filename):
    fig, axs = plt.subplots(2, 2, figsize=(24, 18))

    for i, filename in enumerate(filenames):
        img = plt.imread(filename)
        ax = axs[i // 2, i % 2]
        ax.imshow(img)
        ax.axis('off')

    legend_elements = [
        Line2D([0], [0], color='#1f77b4', lw=10, label='PV'),
        Line2D([0], [0], color='#5f9e8f', lw=10, label='Data Center'),
    ]

    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=26, frameon=False)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    plt.savefig(output_filename, dpi=500, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    path_to_results = r"C:\Users\there\Downloads\results_DC_PV_old"

    df1 = calculate_self_metrics(print_important_params(path_to_results + "/grid_non_shifted.pickle", "Grid connected - Fixed workloads"))
    df2 = calculate_self_metrics(print_important_params(path_to_results + "/off_grid_non_shifted.pickle", "Off Grid - Fixed workloads"))
    df3 = calculate_self_metrics(print_important_params(path_to_results + "/grid_shifted.pickle", "Grid connected - Flexible workloads"))
    df4 = calculate_self_metrics(print_important_params(path_to_results + "/off_grid_shifted.pickle", "Off Grid - Flexible workloads"))

    plot_grouped_bar_with_secondary_star_axis(df1, "a. Grid connected - Fixed workloads", "bar_with_error_grid_noshift.png")
    plot_grouped_bar_with_secondary_star_axis(df2, "b. Off Grid - Fixed workloads", "bar_with_error_offgrid_noshift.png")
    plot_grouped_bar_with_secondary_star_axis(df3, "c. Grid connected - Flexible workloads", "bar_with_error_grid_shifted.png")
    plot_grouped_bar_with_secondary_star_axis(df4, "d. Off Grid - Flexible workloads", "bar_with_error_offgrid_shifted.png")

    combine_plots_with_legend(
        ["bar_with_error_grid_noshift.png", "bar_with_error_offgrid_noshift.png",
         "bar_with_error_grid_shifted.png", "bar_with_error_offgrid_shifted.png"],
        "combined_plot.png"
    )

