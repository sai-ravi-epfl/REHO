from reho.model.reho import *
from reho.plotting import plotting
import numpy as np


if __name__ == '__main__':

    # Set building parameters
    reader = QBuildingsReader()
    n_house = 1
    qbuildings_data = reader.read_csv(buildings_filename='/Users/ravi/Desktop/REHO_fork_ref/scripts/template/data/EPFL_2.csv', nb_buildings= n_house)

    # Select clustering options for weather data
    cluster = {'Location': 'Geneva', 'Attributes': ['T', 'I', 'W'], 'Periods': 10, 'PeriodDuration': 24}
    '''
    file_name = 'C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/waste_heat.csv'
    waste_heat = np.loadtxt(file_name)

    file_name1 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/STC_Tml_district1.csv'
    STC_Tml_district = np.loadtxt(file_name1)

    file_name2 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/Irr_Geneva.csv'
    Irr_Geneva = np.loadtxt(file_name2)
    '''
    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'
    scenario['exclude_units'] = ['HeatPump_Geothermal','HeatPump_Air','HeatPump_Lake','HeatPump_Anergy','HeatPump_DHN', 'ElectricalHeater_SH', 'Battery','ThermalSolar']  #,'ThermalSolar_district''HeatPump'
    scenario["specific"] = []
    scenario['enforce_units'] = ["STES_district"] #'HeatPump_Geothermal_district'
    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {"Cost_demand_cst": 0.08, "Cost_supply_cst": 0.08},
                                            "Heat": {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.02,  "GWP_supply_cst": 0}})  #'NaturalGas': {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.10},
                                                                                                                #"Data": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002}}


    units = infrastructure.initialize_units(scenario, grids, district_data= True)

    parameters = {'Cooling': np.array([1.0]), 'n_vehicles': np.array([0.0]), 'T_DHN_supply_cst': np.repeat(70.0, n_house),'T_DHN_return_cst': np.repeat(60.0, n_house), "TransformerCapacity": np.array([1e8, 0.0])} #, 'Network_supply_heat': np.array([0.0])
    #parameters = {}

    # Set method options
    method = {'building-scale': True, 'use_storage_interperiod':True}
    #parameters = {'T_DHN_supply_cst': np.repeat(70.0, n_house),'T_DHN_return_cst': np.repeat(60.0, n_house),'TransformerCapacity': np.array([1e8,0])}   #'T_DHN_supply_cst': np.repeat(70.0, n_house),'T_DHN_return_cst': np.repeat(60.0, n_house),'TransformerCapacity': np.array([1e8,0])
    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver ='gurobi') #parameters=parameters,
    reho.single_optimization()
    # Save results
    reho.save_results(format=['xlsx', 'pickle'], filename='0')

