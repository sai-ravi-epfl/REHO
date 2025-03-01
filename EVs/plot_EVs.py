from reho.plotting.plotting import *
from matplotlib.lines import Line2D
import warnings
current_folder = Path(__file__).resolve().parent
folder = current_folder / 'results'
warnings.filterwarnings('ignore')
from mpl_axes_aligner import align
import pandas as pd



def get_SS_EVs(bi, uni, costs, era):
    pv_prod = pd.DataFrame([bi[0][i]["df_Annuals"][bi[0][i]["df_Annuals"].index.get_level_values(1).str.contains("PV")].sum().Supply_MWh for i in bi[0]])
    ev_supply = pd.DataFrame([bi[0][i]["df_Unit_t"].xs("EV_district", level=1)["Units_supply"].mul(bi[0][0]["df_Time"].dp).sum() / 1000 for i in bi[0]])
    net_flow = pd.DataFrame([bi[0][i]["df_Annuals"].xs("Network", level=1).Supply_MWh.xs("Electricity") - bi[0][i]["df_Annuals"].xs("Network", level=1).Demand_MWh.xs("Electricity") for i in bi[0]])

    ss_ev_supply = ev_supply / (pv_prod + net_flow)

    n = list(costs.keys())[-1]
    if "EV_district" in bi[0][0]["df_Unit"].index:
        if any(bi[0][0]["df_Unit"].index.str.contains("DHN")):
            uni = pd.read_pickle("results/MC_DHN_EV_uni_0.pickle")
            id = ["LT", "MT", "HT"][n]
            uni = {0: uni.results[id]}

    load = {}
    for i in bi[0]:
        load[i] = bi[0][i]["df_Unit_t"].xs("EV_district", level=1).Units_demand - uni[0][i]["df_Unit_t"].xs("EV_district", level=1).Units_demand
        load[i] = load[i].mul(bi[0][0]["df_Time"].dp)
        load[i] = load[i][load[i] < 0].sum()
    ss_load_shift = -pd.DataFrame(load.values())/1000/(pv_prod + net_flow)

    if "EV_district" in bi[0][0]["df_Unit"].index:
        extra_ss_load = ev_supply * 1000 - pd.DataFrame(load.values())
        if any(bi[0][0]["df_Unit"].index.str.contains("DHN")):
            bi = pd.read_pickle("results/MC_DHN_EV_bi_0.pickle")
            bi = {0: bi.results[id]}
            costs_uni = [uni[0][i]["df_Performance"].xs("Network")[["Costs_op", "Costs_inv"]].sum() for i in uni[0]]
            costs_bi = [bi[0][i]["df_Performance"].xs("Network")[["Costs_op", "Costs_inv"]].sum() for i in bi[0]]
            tariff = (np.array(costs_uni) - np.array(costs_bi))/np.concatenate(extra_ss_load.values)
            print("tariff grid service: ", tariff)
            print("Mean tariff grid service: ", np.mean(tariff[1:]))
            print("Elec cons: ", pv_prod + net_flow)

        elif 1 in costs:
            cost_reduction = (costs[0].sum()[list(range(11))] - costs[1].sum()[list(range(11))]) * era
            tariff = cost_reduction.div(extra_ss_load[0], axis=0)
            print("tariff grid service: ", tariff)
            print("Mean tariff grid service: ", np.mean(tariff[0:]))
            print("Elec cons: ", pv_prod + net_flow)

    return ss_ev_supply, ss_load_shift


def return_ICE_cost(results, scn=0):
    era = results[scn][0]["df_Buildings"]["ERA"].sum()
    ANN = results[scn][0]["df_Performance"].at["Network", "ANN_factor"]
    nb_cars = np.round(era / (1071 / 8.7) / 1.56, 0)
    cars_inv = [10000 * nb_cars * i / 10 * ANN + nb_cars * 20000 * ANN for i in results[scn]] # 20 kCHF fuel, 30 kCHF EVs
    cars_gwp = [177*70 * nb_cars * i / 10 + nb_cars * 7000 for i in results[scn]] # 7 tons fuel, 14 tons EVs

    fuel_costs = 23.8 * 1.56 * 7 / 100 * 2.03 * 365 # km / pers / day * pers / car * l / km * CHF / l * day / yr = CHF/yr/car
    fuel_costs = [fuel_costs * (10 - i) / 10 * nb_cars for i in results[scn]]
    fuel_costs = np.array(fuel_costs / era)

    fuel_gwp = fuel_costs / 1.9 * 2.3 # CHF/yr/car / CHF/l * kg CO2/l = kg CO2/yr/car
    gwp_cars = np.array(cars_gwp)/era/20 + fuel_gwp
    return cars_inv, fuel_costs, gwp_cars


def update_data_capacities(data_cap):
    data_cap.loc["HeatPump"] = data_cap.loc["HeatPump_Air"]+data_cap[data_cap.index.str.contains("ElectricalHeater")].sum()
    col = data_cap.columns[2]
    data_cap = data_cap.loc[~(data_cap[[col]] <= 0.1).all(axis=1)]

    list_remove = list(data_cap[data_cap.index.str.contains("HeatPump")].index) + ["ElectricalHeater_DHW", "ElectricalHeater_SH"]
    data_cap.loc["HeatPump"] = data_cap[data_cap.index.str.contains("HeatPump")].sum()

    if "WaterTankSH" in data_cap.index or "WaterTankDHW" in data_cap.index:
        data_cap.loc["WaterTank"] = data_cap[data_cap.index.str.contains("WaterTank")].sum()
        list_remove = list_remove + ["WaterTankDHW", "WaterTankSH"]

    for key in list_remove:
        try:
            data_cap = data_cap.drop(key)
        except:
            pass

    labels = {"PV": ["PV panel", "#ffd980"], "HeatPump": ["heat pump", "#FEA993"], "DHN_pipes": ["DHN pipe", "#ff6666"],
              "WaterTank": ["water tank", "#B22222"], "NG_Boiler": ["gas boiler", "#770001"], "EV_district": ["vehicles", "lightgreen"]}# "#61e161"
    labels = {key: labels[key] for key in data_cap.index}

    for key in labels:
        data_cap.at[key, ("EN_long", "ColorPastel")] = labels[key]

    if "EV_district" in labels.keys():
        if "DHN_pipes" in labels.keys():
            list_id = ["EV_district", "PV", "HeatPump", "DHN_pipes", "WaterTank", "NG_Boiler"]
        else:
            list_id = ["EV_district", "PV", "HeatPump", "ElectricalHeater", "WaterTank", "NG_Boiler"]
    else:
        list_id = ["PV", "HeatPump", "DHN_pipes", "WaterTank", "NG_Boiler"]

    return data_cap.reindex(list_id).dropna()


def update_labels(data_flow):
    data_flow.at[("revenues", "Electrical_grid_feed_in"), ("EN_long", "ColorPastel")] = ["electricity export", "#b7d2e8"]
    data_flow.at[("costs", "Electrical_grid"), ("EN_long", "ColorPastel")] = ["electricity import", "#74a7d2"]
    data_flow.at[("costs", "NaturalGas"), ("EN_long", "ColorPastel")] = ["gas import", "#3573a6"]
    data_flow.at[("costs", "FossilFuel"), ("EN_long", "ColorPastel")] = ["gasoline import", "#1d3f5c"]
    data_flow = data_flow.iloc[np.r_[0, 1, 2, 5, 4, 3, 6, 7, 8, 9, 10]]
    return data_flow


def add_resources(data_cap, data_flow, merge=True):
    flow_costs = data_flow.xs("costs")

    if "Heat" in flow_costs.index:
        flow_costs = flow_costs.drop("Heat")
    if len(flow_costs) == 3:
        flow_costs = flow_costs.iloc[np.r_[1, 0, 2]]
    if len(flow_costs) == 2:
        flow_costs = flow_costs.iloc[np.r_[1, 0]]

    labels = {"Electrical_grid": ["electricity import", "#74a7d2"], "NaturalGas": ["gas import", "#3573a6"], "Gasoline": ["gasoline import", "#1d3f5c"]}
    labels = {key: labels[key] for key in flow_costs.index}

    for key in labels:
        flow_costs.at[key, ("EN_long", "ColorPastel")] = labels[key]

    flow_revenues = data_flow.xs("revenues").loc[["Electrical_grid_feed_in"]]
    flow_revenues.at["Electrical_grid_feed_in", ("EN_long", "ColorPastel")] = ["electricity export", "#b7d2e8"]

    if merge:
        data_flow = flow_revenues
        data_cap = pd.concat([data_cap, flow_costs])
    else:
        data_flow = pd.concat([flow_revenues, flow_costs])

    return data_cap, data_flow


def plot_stacked_costs(results, era, additional_costs=dict(), additional_gwp=np.array([0]), idx=None, annotations=None, x_label="Share EVs [%]", y_lim=[40, 30], save_name="bi"):

    change_data = pd.DataFrame()
    change_data.index = ['x_axis_1', 'x_axis_2', 'y_axis', 'keyword', 'total', 'unites', 'scc_legend']
    change_data['EN'] = ['CAPEX', 'OPEX', 'Costs [CHF/y]', 'Costs', 'TOTEX', ' CHF', '']

    fig, ax = plt.subplots(1, len(results))
    fig.set_size_inches(11, 6)
    if idx is None:
        idx = np.array(list(results[0][0].keys())) * 10

    costs = {}

    for n, res in enumerate(results):
        df_Economics = dict_to_df(res, 'df_Economics')
        df_costs = df_Economics.xs('costs', level='Perf_type')
        df_costs = df_costs / era.sum()
        change_data.loc['y_axis']['EN'] = "Costs [CHF/m2/y]"

        indexes, data_capacities, data_resources = prepare_dfs(df_costs, "Pareto_ID", neg=True, additional_data=additional_costs, scaling_factor=1)
        data_capacities = update_data_capacities(data_capacities)
        data_capacities, flow_revenues = add_resources(data_capacities, data_resources)
        costs[n] = pd.concat([data_capacities, flow_revenues])

        gwp = [res[0][i]["df_KPIs"]["gwp_tot_m2"].xs("Network") for i in res[0]]
        gwp_tot = np.array(gwp) + additional_gwp

        # plot
        if "EV_district" in res[0][0]["df_Unit"].index and not any(res[0][0]["df_Unit"].index.str.contains("DHN")):
            row = data_capacities.iloc[2:3] * 0
            row.index = [" "]
            row["ColorPastel"] = "white"
            row["EN_long"] = " "
            data_capacities = pd.concat([data_capacities.iloc[:5], row, data_capacities.iloc[5:]])

        if "EV_district" in res[0][0]["df_Unit"].index and any(res[0][0]["df_Unit"].index.str.contains("DHN")):
            row = data_capacities.iloc[2:3] * 0
            row.index = [" "]
            row["ColorPastel"] = "white"
            row["EN_long"] = " "
            data_capacities = pd.concat([data_capacities.iloc[:5], row, data_capacities.iloc[5:]])

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
        ax[n].set_ylim([-5, y_lim[0]])

        ax2 = ax[n].twinx()
        #ax2.plot(idx, gwp_cars, color="#b2b2b2", label="GWP mobility", linewidth=1.0)
        #ax2.plot(idx, gwp, color="#7c7c7c", label="GWP energy system", linewidth=1.0)
        ax2.plot(idx, gwp_tot, label="GWP total", color="Black")
        ax2.set_ylim([0, y_lim[1]])
        if n==len(results)-1:
            ax2.set_ylabel('GWP [kg CO$_2$/m$^2_{ERA}$/yr]', fontsize=16)
           # ax2.spines["right"].set_color("#a40d0d")
            ax2.tick_params(labelsize=12)#, labelcolor="#a40d0d", color="#a40d0d")
        else:
            ax2.tick_params(right=True, labelright=False)
        ax2.tick_params(axis="y", labelsize=12)
        align.yaxes(ax[n], 0, ax2, 0, 0.112)

        ax3 = ax[n].twinx()
        ss = [res[0][i]["df_KPIs"].SS.xs("Network") for i in res[0]]
        sc = [res[0][i]["df_KPIs"].SC.xs("Network") for i in res[0]]

      #  pvp = [res[0][i]["df_KPIs"].PVP.xs("Network") for i in res[0]]
        ax3.plot(idx, [-10]*idx, color="white", label=" ")
        ax3.plot(idx, sc, color="#dbdada", label="self-consumption")
        if "EV_district" in res[0][0]["df_Unit"].index:# and n!=0:
            ss_ev_supply, ss_load_shift = get_SS_EVs(res, results[0], costs, era)
            ax3.plot(idx, ss_load_shift, color="#A9A9A9", linestyle="--", label="self-sufficiency load shift")
            ax3.plot(idx, ss_ev_supply, color="#6b6b6b", linestyle="--", label="self-sufficiency V2G")
        ax3.plot(idx, ss, color="#6b6b6b", label="self-sufficiency")
    #  ax3.plot(idx, pvp, color="#7c7c7c", label="PV penetration")
        ax3.set_ylim([0, 1])
        if n==len(results)-1:
            ax3.spines.right.set_position(("axes", 1+0.1*len(results)))
            ax3.set_ylabel('PV KPI [-]', color="Black", fontsize=16)
            ax3.tick_params(labelsize=12)
            by_label = merge_handles_labels([ax3, ax2, ax[n]])
            fig.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(0.85, 0), frameon=False, ncol=3, fontsize=14)
        else:
            ax3.tick_params(right=False, labelright=False)
        align.yaxes(ax[n], 0, ax3, 0, 0.112)

        annotation = ['(A)', '(B)', '(C)'][n]
        ax[n].text(0, 0.91*y_lim[0], annotation, color="black", fontsize=20)
        if annotations is not None:
            ax[n].text(idx[-1]*0.2*len(results)/3, 0.91*y_lim[0], annotations[n], color="black", fontsize=14)

        ax[n].axhline(y=0, color='black', linestyle='-')
    plt.tight_layout()
    plt.savefig("Figures/" + save_name + ".png", bbox_inches='tight')
    plt.show()
    return

def get_color(name="canard"):
    color = layout[layout.NamePastel == name].ColorPastel.unique()[0]
    return color

def plot():
    tr = [400, 630][1]
    bi = pd.read_pickle("results/dwd_EV_bi_" + str(tr) + ".pickle")
    uni = pd.read_pickle("results/dwd_EV_uni_" + str(tr) + ".pickle")
    if tr == 400:
        uni_extra = pd.read_pickle("results/dwd_EV_uni_" + str(tr) + "_extra.pickle")
        uni[0][7] = uni_extra[0][7]

    era = bi[0][0]["df_Buildings"]["ERA"].sum()
    cars_inv, fuel, gwp_cars = return_ICE_cost(bi)
    additional_costs = {"mobility": fuel}
    for i, j in enumerate(bi[0]):
        bi[0][j]["df_Economics"][("investment", "EV_district")].at["costs", "Network"] = cars_inv[i]
        uni[0][j]["df_Economics"][("investment", "EV_district")].at["costs", "Network"] = cars_inv[i]
    annotations = ["fixed charging profile", "flexible charging profile"]

    plot_stacked_costs([uni, bi], era, additional_costs, gwp_cars, annotations=annotations, save_name="costs_EVs_" + str(tr) + "_kW")

    print("PV capacity: ", bi[0][0]["df_Unit"][bi[0][0]["df_Unit"].index.str.contains("PV")].Units_Mult.sum()/era*1000)
    return


if __name__ =='__main__':
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    plot()




    # plot_pareto_units([bi, uni], KPIs=["SS"], opex_line=True, label="EN_long", title=" ").show()
    # plot_performance(bi, plot='costs', indexed_on='Pareto_ID', label='EN_short', additional_costs=additional_costs).show()
    # plot_performance(uni, plot='costs', indexed_on='Pareto_ID', label='EN_short', additional_costs=additional_costs).show()
    # plot_profiles(uni[0][9], units_to_plot=["PV", "EV_district"]).show()
    # plot_EVs([bi, uni], era, label="EN_long").show()

    # era = dec["pareto"][1]["df_Buildings"].ERA.sum()
    # plot_LCOE([dwd, dec], ["SC", "PVP"], era).show()
    # plot_battery([dwd, dec], era, label="EN_long").show()
    # plt.rcParams.update({'font.size': 10})
    # plot_type = ["demand_feed_in_E_gen_pv", "E_gen_pv_demand_feed_in", "invest_demand_feed_in"][0]
    # bounds = {"feed_in": [0.0, 0.15], "retail": [0.05, 0.25]}
    # plot_rainbow_CH([dwd],  bounds=bounds, resolution=130, std_filter=1.3, plot_type=plot_type)
    # plot_rainbow_CH([dec], bounds=bounds, resolution=130, std_filter=1.3, plot_type=plot_type)





# def plot_battery(results, era, label='FR_long', color='ColorPastel'):
#
#     fig, ax = plt.subplots(1, figsize=(5.5, 4.2))
#     ax2 = ax.twinx()
#
#     for id_res, res in enumerate(results):
#         Scn_id = list(res.keys())[0]
#         E_reimport = []
#         df_unit = dict_to_df(res, 'df_Unit')
#
#         PV = df_unit[df_unit.index.get_level_values('Unit').str.contains('PV')]
#         PV = PV.groupby(level='Pareto_ID', sort=False).sum()/1000
#
#         BAT = df_unit[df_unit.index.get_level_values('Unit').str.contains('Battery')]
#         BAT = BAT.groupby(level='Pareto_ID', sort=False).sum()/1000
#
#         for j in res[Scn_id]:
#             df_el = res[Scn_id][j]["df_Grid_t"].xs("Electricity")["Grid_demand"]
#             delta_elec = df_el.drop(df_el.xs("Network", drop_level=False).index).groupby(["Period", "Time"]).sum() - df_el.xs("Network")
#             delta_elec = delta_elec.groupby("Period").sum().mul(res[Scn_id][1]["df_Time"].dp).sum()/1000
#             E_reimport = E_reimport + [delta_elec]
#
#         style = ["-", "--", ":"][id_res]
#         idx = np.array([res[Scn_id][i]["df_Performance"].xs("Network")["Costs_inv"] for i in res[Scn_id]]) / era
#         ax2.plot(idx, E_reimport, marker='.', linestyle=style, color=layout.loc['Electricity', color], label="E. shared")
#         ax.plot(idx, PV["Units_Mult"], marker='.', linestyle=style, color=layout.loc['PV', color],
#                 label=layout.loc['PV', label] + " [MWp]")
#         ax.plot(idx, BAT["Units_Mult"], marker='.', linestyle=style, color=layout.loc['Battery', color],
#                 label=layout.loc['Battery', label] + " [MWh]")
#
#     # legend system design
#     ax.set_ylabel('capacity [ref size / m$^2$]', color="black")
#     ax.set_xlabel('capital cost [CHF/m$^2$/yr]', color="black")
#     ax2.spines["right"].set_color(layout.loc['Electricity', color])
#     ax2.tick_params(axis='y', colors=layout.loc['Electricity', color])
#     ax2.set_ylabel('shared electricity [MWh]', color=layout.loc['Electricity', color])
#
#     by_label = merge_handles_labels([ax, ax2])
#     ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.1, -0.35), frameon=False, ncol=3)
#
#     axx = ax.twinx()
#     custom_lines = [Line2D([0], [0], color='black', linewidth=1.5),
#                     Line2D([0], [0], color='black', linewidth=1.5, linestyle='--')]
#     axx.legend(custom_lines, ['coordinated', 'uncoordinated'], bbox_to_anchor=(0.9, -0.18), frameon=False,
#                ncol=2, title='system design')
#     axx.set_axis_off()
#     plt.tight_layout()
#
#     return plt
