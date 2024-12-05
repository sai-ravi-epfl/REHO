from reho.model.reho import *
from reho.plotting import plotting
import numpy as np
import pandas as pd


if __name__ == '__main__':

    # Set building parameters
    reader = QBuildingsReader()
    n_house = 1
    qbuildings_data = reader.read_csv(buildings_filename='C:/Users/ettor/Desktop/REHO/scripts/template/data/EPFL_2.csv', nb_buildings= n_house)

    # Select clustering options for weather data
    cluster = {'Location': 'Geneva', 'Attributes': ['T', 'I', 'W'], 'Periods': 10, 'PeriodDuration': 24}

    file_name1 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/STC_Tml_district1.csv'
    STC_Tlm_district = np.loadtxt(file_name1)

    file_name2 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/Irr_Geneva.csv'
    Irr_Geneva = np.loadtxt(file_name2)

    file_name3 = 'C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/demand_cost.csv'
    supply_cost = np.loadtxt(file_name3)
    heat_supply_cst = np.repeat(0.15,242)
    supply_cost = np.append(supply_cost, heat_supply_cst)
    #supply_cost = pd.read_csv(file_name3)


    file_name4 = 'C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/supply_cost.csv'
    demand_cost = np.loadtxt(file_name4)
    heat_demand_cst = np.repeat(0.01, 242)
    demand_cost = np.append(demand_cost, heat_supply_cst)



    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'
    scenario['exclude_units'] = ['HeatPump_Geothermal','ThermalSolar','PV','HeatPump_Air','BESS_IP_district','HeatPump_Lake','HeatPump_Anergy','HeatPump_DHN', 'ElectricalHeater_SH', 'Battery']  #,'ThermalSolar_district''HeatPump'
    scenario["specific"] = []
    scenario['enforce_units'] = ["ThermalSolar_district",'STES_district','HeatPump_Geothermal_district'] #'HeatPump_Geothermal_district'
    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {"Cost_demand_cst": 0.1746, "Cost_supply_cst": 0.3346},
                                            "Heat": {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.15}})  #'NaturalGas': {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.10},
                                                                                                                #"Data": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002}}

    #grids = infrastructure.initialize_grids({'Electricity': {"Cost_demand_cst": demand_cost, "Cost_supply_cst": supply_cost},
                                            #"Heat": {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.15}})


    units = infrastructure.initialize_units(scenario, grids, district_data= True)

    parameters = {'n_vehicles': np.array([0.0]), 'T_DHN_supply_cst': np.repeat(70.0, n_house),'T_DHN_return_cst': np.repeat(60.0, n_house),
                  "TransformerCapacity": np.array([1e8, 0]), 'TransformerCapacity_heat':np.array([0]),
                  'STC_Tlm_district': STC_Tlm_district,'I_global_STC': Irr_Geneva,'Cost_supply_network':supply_cost, 'Cost_demand_network': demand_cost} #'Cost_demand_network': demand_cost,'Cost_supply_network':supply_cost


    # Set method options
    method = {'building-scale': True, 'use_storage_interperiod':True}
    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver ='gurobi') #parameters=parameters,
    reho.single_optimization()
    # Save results
    reho.save_results(format=['xlsx', 'pickle'], filename='0')

    plotting.plot_storage_profile_stes(reho.results['totex'][0], resolution='daily').show()


    units_to_plot = ['STES_district', 'ThermalSolar_district', 'HeatPump_Geothermal_district']
    plotting.plot_energy_balance_for_STES(reho.results['totex'][0], units_to_plot, color='ColorPastel', day_of_the_year= 348, time_range='3days',label='EN_long').show()

    plotting.plot_c_d_STES(reho.results['totex'][0]).show()
