import os
from reho.plotting.plotting import *
from matplotlib.lines import Line2D
import warnings
current_folder = Path(__file__).resolve().parent
folder = current_folder / 'results'
warnings.filterwarnings('ignore')
from mpl_axes_aligner import align
import pandas as pd
from scipy.interpolate import make_interp_spline
import numpy as np


def extract_pareto_ID_list(data):

    """Extracts necessary data for stacked plots from the pickle file."""
    pareto_ids = list(data['gwp'].keys())

    # Initialize storage for extracted values
    extracted = {
        "Data_Production": [],
        "Data_Outsourced": [],
        "Data_Percentage_Inhouse": [],
        "Pareto_ID": []
    }

    costs = {}

    for pid in pareto_ids:
        df_annuals = data['gwp'][pid]['df_Annuals']
        data_production = df_annuals.xs("DataCentre_EPFL_district", level=1).Supply_MWh.xs("Data")
        data_outsourced = df_annuals.xs("Network", level=1).Supply_MWh.xs("Data")
        # Calculate percentage of data processed in-house
        if (data_production + data_outsourced) > 0:
            percent_data_inhouse = (data_production / (data_production + data_outsourced)) * 100
        else:
            percent_data_inhouse = 0
        # Store extracted values
        extracted["Pareto_ID"].append(pid)
        extracted["Data_Production"].append(data_production)
        extracted["Data_Outsourced"].append(data_outsourced)
        extracted["Data_Percentage_Inhouse"].append(percent_data_inhouse)

    # Convert to DataFrame for easier sorting later
    df_extracted = pd.DataFrame(extracted)

    # Sort the data by percentage of data processed in-house
    df_extracted.sort_values(by="Data_Percentage_Inhouse", inplace=True)

    pareto_id_list = df_extracted["Pareto_ID"].tolist()

    return pareto_id_list


def get_heat_ratio_df(results):
    heat_ratio_df = pd.DataFrame()

    for n, res in enumerate(results):
        heat_ratios = {}

        for i in res['gwp']:  # Loop over all indexed keys in `bi['gwp']`
            df_annuals = res['gwp'][i]["df_Annuals"]
            df_annuals = pd.DataFrame(df_annuals)

            # Extract total heat demand in buildings
            buildings = [f'DHN_hex_in_Building{j}' for j in range(1, 25)]
            df_heat_buildings = df_annuals.loc[
                (df_annuals.index.get_level_values('Layer') == 'Heat') &
                (df_annuals.index.get_level_values('Hub').isin(buildings))
            ]
            #total_demand_mwh = df_heat_buildings['Demand_MWh'].sum() if not df_heat_buildings.empty else 0
            total_demand_mwh = 29098.4483 # from the energy heating and hot water signatures
            # Extract heat supplied by data center
            df_heat_DC = df_annuals.loc[
                (df_annuals.index.get_level_values('Layer') == 'Heat') &
                (df_annuals.index.get_level_values('Hub') == 'DataCentre_EPFL_district')
            ]
            total_Heat_DataCentre_EPFL_district = df_heat_DC['Supply_MWh'].sum() if not df_heat_DC.empty else 0

            # Extract heat demand of ORC
            df_heat_DC_ORC = df_annuals.loc[
                (df_annuals.index.get_level_values('Layer') == 'Heat') &
                (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')
            ]
            total_DC_ORC_demand_mwh = df_heat_DC_ORC['Demand_MWh'].sum() if not df_heat_DC_ORC.empty else 0

            # Extract elec supply of ORC
            df_elec_DC_ORC = df_annuals.loc[
                (df_annuals.index.get_level_values('Layer') == 'Electricity') &
                (df_annuals.index.get_level_values('Hub') == 'ORC_EPFL_district')
            ]
            total_DC_ORC_supply_mwh = df_elec_DC_ORC['Supply_MWh'].sum() if not df_heat_DC_ORC.empty else 0

            # Heat directly supplied
            DC_direct_heat_supply_mwh = total_Heat_DataCentre_EPFL_district - total_DC_ORC_demand_mwh

            # Extract heat supply from data center heat pump
            df_heat_supply_DC_HP = df_annuals.loc[
                (df_annuals.index.get_level_values('Layer') == 'Heat') &
                (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')
            ]

            total_DC_HP_supply_mwh = df_heat_supply_DC_HP['Supply_MWh'].sum() if not df_heat_supply_DC_HP.empty else 0


            # Extract elec demand from data center heat pump
            df_elec_demand_DC_HP = df_annuals.loc[
                (df_annuals.index.get_level_values('Layer') == 'Electricity') &
                (df_annuals.index.get_level_values('Hub') == 'HeatPump_DataCentre_district')
                ]

            total_DC_HP_elec_demand_mwh = df_elec_demand_DC_HP['Demand_MWh'].sum() if not df_elec_demand_DC_HP.empty else 0

            # Heat supply of  the main heat pump
            df_heat_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Heat') &
                                        (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
            total_HP_supply_mwh = df_heat_HP['Supply_MWh'].sum()


            # Elec demand of  the main heat pump
            df_elec_HP = df_annuals.loc[(df_annuals.index.get_level_values('Layer') == 'Electricity') &
                                        (df_annuals.index.get_level_values('Hub') == 'HeatPump_Geothermal_district')]
            total_HP_demand_mwh = df_elec_HP['Demand_MWh'].sum()

            #COP_geothermal = total_HP_supply_mwh/total_HP_demand_mwh
            COP_geothermal = 3
            COP_HP_DC = 4.3
            # Compute Heat Ratio (Q_DC / Q_building)
            #if DC_direct_heat_supply_mwh == 0:
            total_Q_DC = 0.7*COP_geothermal*(total_DC_ORC_supply_mwh- (total_DC_HP_supply_mwh/COP_HP_DC) ) + DC_direct_heat_supply_mwh + total_DC_HP_supply_mwh
            #else:
            #    total_Q_DC = DC_direct_heat_supply_mwh + 0.7* total_DC_ORC_supply_mwh *COP_geothermal
            heat_ratio = total_Q_DC / total_demand_mwh if total_demand_mwh > 0 else 0

            # Store results in dictionary
            heat_ratios[i] = heat_ratio

        # Convert dictionary to DataFrame with correct structure
        heat_ratio_df[n] = pd.Series(heat_ratios)

    return heat_ratio_df


def update_data_capacities(data_cap):
    data_cap.loc["HeatPump_Geothermal_district"] = data_cap.loc["HeatPump_Geothermal_district"]+data_cap[data_cap.index.str.contains("ElectricalHeater")].sum()
    col = data_cap.columns[3]
    data_cap = data_cap.loc[~(data_cap[[col]] <= 0.1).all(axis=1)]
    heatpump_filter = data_cap.index.str.contains("HeatPump") & ~data_cap.index.str.contains("HeatPump_DataCentre_district")
    #list_remove = list(data_cap[data_cap.index.str.contains("HeatPump")].index) + ["ElectricalHeater_DHW", "ElectricalHeater_SH", 'DHN_hex',"DHN_pipes"]

    list_remove = list(data_cap[heatpump_filter].index) + ["ElectricalHeater_DHW","ElectricalHeater_SH", 'DHN_hex',"DHN_pipes", 'DataHeat_DHW']
    #data_cap.loc["HeatPump"] = data_cap[data_cap.index.str.contains("HeatPump")].sum()
    data_cap.loc["HeatPump"] = data_cap[heatpump_filter].sum()

    if "WaterTankSH" in data_cap.index or "WaterTankDHW" in data_cap.index:
        data_cap.loc["WaterTank"] = data_cap[data_cap.index.str.contains("WaterTank")].sum()
        list_remove = list_remove + ["WaterTankDHW", "WaterTankSH"]

    for key in list_remove:
        try:
            data_cap = data_cap.drop(key)
        except:
            pass

    labels = {"PV": ["PV panel", "#ffd980"], "HeatPump": ["Heat pump", "#FEA993"], "DHN_pipes": ["DHN pipe", "#ff6666"],
              "WaterTank": ["Water tank", "#B22222"], "NG_Boiler": ["Gas boiler", "#770001"], "DataCentre_EPFL_district": ["Data Center", "#D2B48C"],"ORC_EPFL_district": ["Organic Rankine Cycle", "crimson"],"HeatPump_DataCentre_district": ["Heat Pump (ORC rejected heat source)", "crimson"], "Battery_district": ["District level Battery", "#61e161"],"PV_district": ["District level PV", '#01796F']}# "#61e161"
    labels = {key: labels[key] for key in data_cap.index}

    for key in labels:
        data_cap.at[key, ("EN_long", "ColorPastel")] = labels[key]

    if "EV_district" in labels.keys():
        if "DHN_pipes" in labels.keys():
            #ist_id = ["DataCentre_EPFL_district", "EV_district", "PV", "HeatPump", "DHN_pipes", "WaterTank", "NG_Boiler"]
            list_id = ["DataCentre_EPFL_district", "PV", "HeatPump", "DHN_pipes", "WaterTank", "ORC_EPFL_district",
                       'HeatPump_DataCentre_district', 'Battery_district']
        else:
            #list_id = ["EV_district", "PV", "HeatPump", "ElectricalHeater", "WaterTank", "NG_Boiler"]
            list_id = ["DataCentre_EPFL_district", "PV", "HeatPump", "DHN_pipes", "WaterTank", "ORC_EPFL_district",
                       'HeatPump_DataCentre_district', 'Battery_district']
    else:
        list_id = ["DataCentre_EPFL_district", "PV", "HeatPump", "DHN_pipes", "WaterTank", "ORC_EPFL_district", 'HeatPump_DataCentre_district', 'Battery_district', 'PV_district']

    return data_cap.reindex(list_id).dropna()


def add_resources(data_cap, data_flow, merge=True):
    flow_costs = data_flow.xs("costs")

    if "Heat" in flow_costs.index:
        flow_costs = flow_costs.drop("Heat")
    if len(flow_costs) == 3:
        flow_costs = flow_costs.iloc[np.r_[1, 0, 2]]
    if len(flow_costs) == 2:
        flow_costs = flow_costs.iloc[np.r_[1, 0]]

    labels = {"Electrical_grid": ["Electricity import", "#74a7d2"], "NaturalGas": ["Gas import", "#3573a6"], "Data": ["Data import", "#1d3f5c"]}
    labels = {key: labels[key] for key in flow_costs.index}

    for key in labels:
        flow_costs.at[key, ("EN_long", "ColorPastel")] = labels[key]

    flow_revenues = data_flow.xs("revenues").loc[["Electrical_grid_feed_in"]]
    flow_revenues.at["Electrical_grid_feed_in", ("EN_long", "ColorPastel")] = ["Electricity export", "#b7d2e8"]

    if merge:
        data_flow = flow_revenues
        data_cap = pd.concat([data_cap, flow_costs])
    else:
        data_flow = pd.concat([flow_revenues, flow_costs])

    return data_cap, data_flow


def plot_stacked_costs(results, era, additional_costs=dict(), additional_gwp=np.array([0]), idx=None, annotations=None, x_label= "Data Center Size [%]", y_lim=[55, 200, 1.0], save_name="bi", pareto_ids = 32):

    change_data = pd.DataFrame()
    change_data.index = ['x_axis_1', 'x_axis_2', 'y_axis', 'keyword', 'total', 'unites', 'scc_legend']
    change_data['EN'] = ['CAPEX', 'OPEX', 'Costs [CHF/y]', 'Costs', 'TOTEX', ' CHF', '']

    fig, ax = plt.subplots(1, len(results))
    fig.set_size_inches(8, 7)

    if len(results) == 1:
        ax = [ax]

    if idx is None:
        #idx = np.array(list(results[0]['gwp'].keys())) * 10
        #idx = np.array([1,2,3,4,5,6,7,8,9,10]) * 10
        idx = np.linspace(0, 100,  len(results[0]['gwp'].keys()))
    costs = {}

    for n, res in enumerate(results):
        df_Economics = dict_to_df(res, 'df_Economics')
        df_costs = df_Economics.xs('costs', level='Perf_type')
        df_costs = df_costs / era.sum()
        change_data.loc['y_axis']['EN'] = "Costs [CHF/m2/y]"

        indexis, data_capacities, data_resources = prepare_dfs(df_costs, "Pareto_ID", neg=True, additional_data=additional_costs, scaling_factor=1)


        data_capacities = update_data_capacities(data_capacities)
        data_capacities, flow_revenues = add_resources(data_capacities, data_resources)
        costs[n] = pd.concat([data_capacities, flow_revenues])
        if pareto_ids == 32:
            indexes = [0, 5, 8, 12, 15, 18, 22, 25, 28, 31]
        if pareto_ids == 8:
            indexes = [0,1,2,3,4,5,6,7]
        if pareto_ids == 6:
            indexes = [0,1,2,3,4,5]
        if pareto_ids == 10:
            indexes = [0,1,2,3,4,5,6,7,8,9]
        gwp = [res['gwp'][i]["df_KPIs"]["gwp_tot_m2"].xs("Network") for i in indexes]
        gwp_tot = np.array(gwp) + additional_gwp



        ax[n].stackplot(idx, data_capacities[indexes], baseline="zero", alpha=0.95, colors=data_capacities["ColorPastel"], labels=data_capacities["EN_long"])
        ax[n].stackplot(idx, flow_revenues[indexes], baseline="zero", alpha=0.95, colors=flow_revenues["ColorPastel"], labels=flow_revenues["EN_long"])
        if len(x_label) > 20:
            if n == 1:
                ax[n].set_xlabel(x_label, fontsize=18)
        else:
            ax[n].set_xlabel(x_label, fontsize=18)
        if n==0:
            ax[n].set_ylabel("Costs [CHF/m$^2_{ERA}$/yr]", fontsize=18)
            ax[n].tick_params(axis='y', labelbottom=False)
        else:
            ax[n].tick_params(left=False, labelleft=False)
        ax[n].tick_params(axis="both", labelsize=12)
        ax[n].set_ylim([-0.5, y_lim[0]])

        ax2 = ax[n].twinx()
        #ax2.plot(idx, gwp_cars, color="#b2b2b2", label="GWP mobility", linewidth=1.0)
        #ax2.plot(idx, gwp, color="#7c7c7c", label="GWP energy system", linewidth=1.0)
        ax2.plot(idx, gwp_tot, label="GWP total", color="Black")

        if n==len(results)-1:
            ax2.set_ylabel('GWP [kg CO$_2$/m$^2_{ERA}$/yr]', fontsize=16)
           # ax2.spines["right"].set_color("#a40d0d")
            ax2.tick_params(labelsize=12)#, labelcolor="#a40d0d", color="#a40d0d")
        else:
            ax2.tick_params(right=True, labelright=False)
        ax2.tick_params(axis="y", labelsize=12)
        align.yaxes(ax[n], 0, ax2,5 , 0.112)
        ax2.set_ylim([-24.9, y_lim[1]])



        ax[n].axhline(y=0, color='black', linestyle='-')

        # Gewünschte Reihenfolge der Legendenlabels
        desired_order = [
            "Data import",
            "Electricity import",
            "Electricity export",
            "Data Center",
            "District level Battery",
            "District level PV",
            "PV panel",
            "Heat pump",
            "GWP total",
            "Heat Ratio"
        ]

        # Handles und Labels sammeln
        handles, labels = [], []
        for axis in [ax[n], ax2]:  # oder deine Achsenliste
            h, l = axis.get_legend_handles_labels()
            for handle, label in zip(h, l):
                if label not in labels:
                    handles.append(handle)
                    labels.append(label)

        # Mapping von Label zu Handle
        label_to_handle = dict(zip(labels, handles))

        # Sortieren nach gewünschter Reihenfolge
        sorted_labels = [label for label in desired_order if label in label_to_handle]
        sorted_handles = [label_to_handle[label] for label in sorted_labels]

    # Layout und Legende
    fig.tight_layout(rect=[0, 0.15, 1, 1])
    fig.legend(sorted_handles, sorted_labels, loc='lower center', bbox_to_anchor=(0.5, -0.019),ncol=3, fontsize=14, frameon=False)

        #plt.show()
        # Set the final combined legend
        #fig.legend(handles, labels, loc='lower center', ncol=3, fontsize=12)

    # Adjust bottom margin to prevent legend clipping
    # Adjust the subplot parameters to add white space
    #plt.subplots_adjust(left = 0.2,right = 0.25, top=0.95, bottom=0.25)
    #plt.tight_layout()
    plt.savefig(os.getcwd() +"/"+ save_name + ".png")
    plt.show()
    return

def get_color(name="canard"):
    color = layout[layout.NamePastel == name].ColorPastel.unique()[0]
    return color

def plot():

    #bi = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_HP_Pareto_T_S.pickle")
    #bi = pd.read_pickle(os.getcwd() + "/results/EPFL_BAU_Pareto_CI.pickle")
    #bi = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_HP_Pareto_T_NS.pickle")
    #bi = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_HP_Pareto_T_NS_inequality.pickle")
    #bi = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_HP_Pareto_T_S_inequality.pickle")
    #bi = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_HP_Pareto_CI.pickle")
    bi = pd.read_pickle(os.getcwd() + "/results/EPFL_BAU_Pareto_CI.pickle")

    # Your desired key order list
    #ORC_HP = [12, 28, 4, 20, 0, 16, 8, 24, 14, 30, 6, 22, 2, 18, 10, 26,9, 25, 1, 17, 5, 21, 13, 29, 11, 27, 3, 19, 7, 23, 15, 31]

    ORC_HP = extract_pareto_ID_list(bi)

    # Create a new dictionary with the keys in the specified order
    bi['gwp'] = {key: bi['gwp'][key] for key in ORC_HP if key in bi['gwp']}

    bi['gwp'] = {new_key: bi['gwp'][old_key] for new_key, old_key in enumerate(bi['gwp'].keys(), start=0)}

    #uni = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_Pareto_T_S.pickle")
    #uni = pd.read_pickle(os.getcwd() + "/results/EPFL_BAU_Pareto_CI.pickle")
    #uni = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_Pareto_T_NS.pickle")
    #uni = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_Pareto_T_NS_inequality.pickle")
    #uni = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_Pareto_T_S_inequality.pickle")
    #uni = pd.read_pickle(os.getcwd() + "/results/EPFL_ORC_Pareto_CI.pickle")
    uni = pd.read_pickle(os.getcwd() + "/results/EPFL_BAU_Pareto_CI.pickle")
    # ORC = [4, 20, 28, 12, 16, 0, 8, 24, 26, 10, 2, 18, 14, 30, 22, 6,11, 27, 19, 3, 31, 15, 7, 23, 21, 5, 13, 29, 9, 25, 1, 17]

    ORC = extract_pareto_ID_list(uni)

    uni['gwp'] = {key: uni['gwp'][key] for key in ORC if key in uni['gwp']}

    uni['gwp'] = {new_key: uni['gwp'][old_key] for new_key, old_key in enumerate(uni['gwp'].keys(), start=0)}

    era = bi['gwp'][0]["df_Buildings"]["ERA"].sum()
    #cars_inv, fuel, gwp_cars = return_ICE_cost(bi)

    annotations = ["Legacy Heat Recovery", "Exergy-Aware Heat Recovery"]

    plot_stacked_costs([uni], era, annotations=annotations, save_name="EPFL_BAU", pareto_ids= len(list(uni['gwp'].keys())) )

    #print("PV capacity: ", bi['gwp'][0]["df_Unit"][bi['gwp'][0]["df_Unit"].index.str.contains("PV")].Units_Mult.sum()/era*1000)
    return


if __name__ =='__main__':
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    plot()

