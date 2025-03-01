from reho.model.reho import *
from reho.model.preprocessing.clustering import Clustering

if __name__ == '__main__':

    # Set building parameters
    # you can as well define your district from a csv file instead of reading the database
    reader = QBuildingsReader()
    n_house = 1
    file_ID = "/EPFL_MOES.csv"
    epfl_csv_path = path_to_buildings_csv + file_ID
    qbuildings_data = reader.read_csv(buildings_filename=epfl_csv_path, nb_buildings= n_house)

    # Select weather data
    cluster = {'Location': 'Pully', 'Attributes': ['I', 'T'], 'Periods': 14, 'PeriodDuration': 24, 'custom_weather': path_to_profiles + '/pully.csv' }
    data_centre_heat_profile = np.repeat(50, 338)

    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'gwp'
    scenario['exclude_units'] = ['HeatPump_Geothermal','HeatPump_Air','HeatPump_Lake','HeatPump_Anergy','HeatPump_DHN', 'ElectricalHeater_SH', 'ThermalSolar', 'Battery', 'DHN_out_district','STES_district', 'DataHeat_DHW'] #'OIL_Boiler',  'NG_Boiler','HeatPump_Air', 'HeatPump_Lake''HeatPump_Anergy''DataHeatSH',
    scenario['enforce_units'] = ['DataHeat_SH'] #'HeatPump_Geothermal_district','DHN_out_district','Battery_district','PV_district','ORC_EPFL_district'
    scenario["specific"] = ["enforce_PV_max"]

    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {"Cost_demand_cst": 0.08, "Cost_supply_cst": 0.20},
                                             "Data": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002},
                                             "Heat": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002,  "GWP_supply_cst": 0}})  #'NaturalGas': {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.10},
                                                                                                                #"Data": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002}}


    units = infrastructure.initialize_units(scenario, grids, district_data= True)
    parameters = {'n_vehicles': np.array([0.0]), 'T_DHN_supply_cst': np.repeat(70.0, n_house),'T_DHN_return_cst': np.repeat(60.0, n_house),'TransformerCapacity': np.array([1e8,1e8,0]),'data_EUD': data_centre_heat_profile}


    # Set method options
    method = {'building-scale': True,'save_stream_t': True, 'use_dynamic_emission_profiles': True, 'save_streams': True,'ORC_all_the_time': True} #, 'use_pv_orientation': True
    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver ='gurobi') #parameters=parameters,
    reho.single_optimization()

    # Save results
    filename='testing_DC'
    reho.save_results(format=['xlsx','pickle'], filename=filename)
