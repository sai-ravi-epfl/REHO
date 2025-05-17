from reho.model.reho import *
from reho.plotting import plotting
from reho.model.postprocessing.sensitivity_analysis import *
from reho.model.preprocessing.clustering import Clustering

if __name__ == '__main__':

    # Set building parameters
    # you can as well define your district from a csv file instead of reading the database
    reader = QBuildingsReader()
    n_house = 1
    file_ID =  "/EPFL_MOES.csv"
    epfl_csv_path = path_to_buildings_csv + file_ID
    qbuildings_data = reader.read_csv(buildings_filename=epfl_csv_path, nb_buildings= n_house)

    # Select weather data
    cluster = {'Location': 'Pully', 'Attributes': ['I', 'T', 'D','E', 'CS'], 'Periods': 14, 'PeriodDuration': 24, 'custom_weather': path_to_profiles + '/pully.csv' } #
    attributes = ['Irr', 'Text', 'DataLoad','Emissions', 'Cost_supply_elec'] #,'Cost_supply_elec'
    weather_file = path_to_profiles + '/pully.csv'
    weather.data_centre_profile(size=10000, shifted = True)
    df_annual = weather.read_custom_weather(weather_file, weeks = cluster['PeriodDuration'] ==168)
    df_annual = df_annual[attributes]
    nb_clusters = [cluster['Periods']]
    cl = Clustering(data=df_annual, nb_clusters=nb_clusters, option={"year-to-day": True, "extreme": []}, pd=cluster['PeriodDuration'])
    cl.run_clustering()
    val_cls = weather.generate_output_data(cl, attributes, "Pully",cluster)
    data_centre_heat_profile = weather.data_centre_profiles(val_cls)
    temp_profile, irr_profile = weather.temp_irr_profiles(val_cls)
    #data_profile_buildings = np.tile(data_centre_heat_profile/nb_clusters[0], nb_clusters[0])

    # Set scenario
    scenario = dict()

    #scenario['Objective'] = ['OPEX', 'CAPEX']
    #scenario['nPareto'] = 2
    #scenario['name'] = 'gwp'

    scenario['Objective'] = 'OPEX'
    scenario['name'] = 'gwp'
    scenario['exclude_units'] = ['HeatPump_Geothermal','HeatPump_Air','HeatPump_Lake','HeatPump_Anergy',
                                 'ThermalSolar', 'Battery', 'DHN_out_district','STES_district', 'DataHeat_DHW','DataHeat_SH'] #'OIL_Boiler',  'NG_Boiler','HeatPump_Air', 'HeatPump_Lake''HeatPump_Anergy''DataHeatSH',

    scenario['enforce_units'] = [] #'HeatPump_Geothermal_district','DHN_out_district','Battery_district','PV_district','ORC_EPFL_district'
    scenario["specific"] = ['enforce_DHN']

    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {},#"Cost_demand_cst": 0.08, "Cost_supply_cst": 0.20
                                             "Data": {},#"Cost_demand_cst": 0.0, "Cost_supply_cst": 0.26
                                             "Heat": {},
                                             })  #'NaturalGas': {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.10},"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002,  "GWP_supply_cst": 0
                                                                                                                #"Data": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002}}


    units = infrastructure.initialize_units(scenario, grids, district_data= True)
    parameters = {'n_vehicles': np.array([0.0]), 'T_DHN_supply_cst': np.repeat(67.0, n_house),'T_DHN_return_cst': np.repeat(55.0, n_house),'TransformerCapacity': np.array([1e8,0,0]),'data_EUD': data_centre_heat_profile, 'T_ext' : temp_profile , 'I_global': irr_profile}

    # Set method options
    method = {'district-scale': True,'save_stream_t': True, 'use_dynamic_emission_profiles': True, 'save_streams': True, "Link_DC_to_district_PV": True, 'ORC_all_the_time':True} #, 'use_pv_orientation': True
    DW_params = {'max_iter': 1}
    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver ='gurobi', DW_params = DW_params) #parameters=parameters,
    #reho.generate_pareto_curve()
    reho.single_optimization()


    '''
    SA = SensitivityAnalysis(reho, SA_type="Monte_Carlo", sampling_parameters= 4)
    SA_parameters = {'Data_GWP': np.array([0,5 ])} #, 'Data_cap':np.array([0, 20000])'PV_cap': np.array([0, 100000])
    SA.build_SA([], SA_parameters=SA_parameters)
    SA.run_SA()
    '''

    # Save results_
    #filename='EPFL_ORC_HP_Pareto_T_NS_inequality'
    filename= 'Sai_shift_off_grid'
    print("Datacentre size",reho.results['gwp'][0]['df_Unit'].xs('DataCentre_EPFL_district')['Units_Mult'])
    print("PV size", reho.results['gwp'][0]['df_Unit'].xs('PV_district')['Units_Mult'])
    #print("NG generator", reho.results['gwp'][0]['df_Unit'].xs('NG_generator_district')['Units_Mult'])
    reho.save_results(format=['pickle'], filename=filename)


    #plotting.plot_performance(reho.results, plot='costs', indexed_on='Scn_ID', label='EN_long').show()
    #plotting.plot_performance(reho.results, plot='gwp', indexed_on='Scn_ID', label='EN_long').show()
    #plotting.plot_sankey(reho.results['gwp'][0], label='EN_long', color='ColorPastel').show()
    # Construct the full file path
    # plotting.yearly_demand_plot(filename)

    # path_egid_map =
    # Read typical day distribution and buildings profiles

