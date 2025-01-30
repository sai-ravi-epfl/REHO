from reho.model.reho import *
from reho.plotting import plotting
import numpy as np
import pandas as pd


if __name__ == '__main__':

    # Set building parameters
    reader = QBuildingsReader()
    n_house = 24
    qbuildings_data = reader.read_csv(buildings_filename='C:/Users/ettor/Desktop/REHO/scripts/template/data/EPFL_MOES.csv', nb_buildings= n_house)

    # Select clustering options for weather data
    cluster = {'Location': 'Geneva', 'Attributes': ['T', 'I', 'W'], 'Periods': 10, 'PeriodDuration': 24}

    file_name1 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/STC_Tml_district1.csv'
    STC_Tlm_district = np.loadtxt(file_name1)

    file_name2 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/Irr_Geneva.csv'
    Irr_Geneva = np.loadtxt(file_name2)

    
    file_name5 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/STC_efficiency_district.csv'
    STC_efficiency_district = np.loadtxt(file_name5)

    file_name6 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/waste_heat.csv'
    Waste_heat = np.loadtxt(file_name6)

    file_name7 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/Text_geneva.csv'
    Text_Geneva = np.loadtxt(file_name7)





    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'
    scenario['exclude_units'] = ['ThermalSolar','ElectricalHeater_DHW','Battery_district','HeatPump_Air','BESS_IP_district','HeatPump_Lake','HeatPump_Anergy','HeatPump_Geothermal','HeatPump_DHN', 'ElectricalHeater_SH', 'Battery']
    scenario["specific"] = []
    scenario['enforce_units'] = ['STES_district','ThermalSolar_district','HeatPump_Geothermal_district','PV'] #'HeatPump_Geothermal_district' 'STES_district','ThermalSolar_district'
    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {"Cost_demand_cst": 0.1746, "Cost_supply_cst": 0.3346},
                                            "Heat": {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.15}})  #'NaturalGas': {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.10},
                                                                                                                #"Data": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002}}

    #grids = infrastructure.initialize_grids({'Electricity': {"Cost_demand_cst": demand_cost, "Cost_supply_cst": supply_cost},
                                            #"Heat": {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.15}})


    units = infrastructure.initialize_units(scenario, grids, district_data= True)

    parameters = {'n_vehicles': np.array([0.0]), 'T_DHN_supply_cst': np.repeat(70.0, n_house),'T_DHN_return_cst': np.repeat(60.0, n_house),
                  'STC_Tlm_district': STC_Tlm_district,'I_global_STC': Irr_Geneva, 'STC_efficiency_district': STC_efficiency_district, 'Text_Geneva': Text_Geneva,
                  'TransformerCapacity_supply': np.array([1e8,0]),'TransformerCapacity_demand': np.array([1e8,0]) }


    # Set method options
    method = {'building-scale': True, 'use_storage_interperiod':True}
    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver ='gurobi') #parameters=parameters,
    reho.single_optimization()
    # Save results
    reho.save_results(format=['xlsx', 'pickle'], filename='no_T_const')

    plotting.plot_SOC_STES(reho.results['totex'][0], resolution='daily').show()

    #'ThermalSolar_district',
    units_to_plot = ['ThermalSolar_district','STES_district',  'PV', 'HeatPump_Geothermal_district']
    plotting.plot_energy_balance_for_STES(reho.results['totex'][0], units_to_plot, color='ColorPastel', day_of_the_year= 335, time_range='',label='EN_long').show()

    plotting.plot_c_d_STES(reho.results['totex'][0]).show()


