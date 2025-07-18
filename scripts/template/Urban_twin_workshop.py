from reho.model.reho import *
from reho.paths import path_to_profiles
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
    cluster = {'Location': 'Pully', 'Attributes': ['I', 'T','E','D','CS'], 'Periods': 14, 'PeriodDuration': 24}
    attributes = ['Irr', 'Text', 'Emissions','DataLoad', 'Cost_supply_elec']
    weather_file = path_to_profiles+'/pully.csv'
    weather.data_centre_profile(size = 10000)
    df_annual = weather.read_custom_weather(weather_file, weeks = cluster['PeriodDuration'] ==168)
    df_annual = df_annual[attributes]
    nb_clusters = [cluster['Periods']]
    cl = Clustering(data=df_annual, nb_clusters=nb_clusters, option={"year-to-day": True, "extreme": []}, pd=cluster['PeriodDuration'])
    cl.run_clustering()
    val_cls = weather.generate_output_data(cl, attributes, "Pully",cluster)
    data_centre_heat_profile = weather.data_centre_profiles(val_cls)
    temp_profile, irr_profile = weather.temp_irr_profiles(val_cls)

    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'
    #scenario['Objective'] = ['OPEX', 'CAPEX']
    #scenario['nPareto'] = 4
    #scenario['name'] = 'gwp'
    scenario['exclude_units'] = ['HeatPump_Geothermal','HeatPump_Anergy','HeatPump_DHN', 'ElectricalHeater_SH', 'ThermalSolar', 'Battery','HeatPump_Lake',
                                 'HeatPump_Air','ORC_EPFL_district','STES_district','HeatPump_DataCentre_district','DHN_out_district',"data_consumer_district", 'PV_district','DataHeat_DHW','DataHeat_SH'] #'OIL_Boiler',  'NG_Boiler','HeatPump_Air', 'HeatPump_Lake''HeatPump_Anergy''DataHeatSH',
    #
    scenario['enforce_units'] = ['Battery_district']
    #scenario["specific"] = ["enforce_PV_max"]


    grids = infrastructure.initialize_grids({'Electricity': {},'Data': {},
                                            "Heat": {}})

    units = infrastructure.initialize_units(scenario, grids, district_data= True)
    DW_params = {'max_iter': 2}
    parameters = {'n_vehicles': np.array([0.0]), 'T_DHN_supply_cst': np.repeat(67.0, n_house),'T_DHN_return_cst': np.repeat(55.0, n_house),  'data_EUD': data_centre_heat_profile, "TransformerCapacity": np.array([1e8,1e8, 0]),  'DC_heat_recovery': 0, 'T_ext' : temp_profile , 'I_global': irr_profile} #, 'Network_supply_heat': np.array([0.0])

    # Set method options
    method = {'district-scale': True,'save_stream_t': True, 'use_dynamic_emission_profiles': True, 'save_streams': True,'ORC_all_the_time': False} #, 'use_pv_orientation': True
    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver ='gurobi', DW_params=DW_params) #parameters=parameters,
    #reho.generate_pareto_curve()
    reho.single_optimization()

    # Save results
    filename='example_datacenter'
    reho.save_results(format=['xlsx', 'pickle'], filename=filename)

