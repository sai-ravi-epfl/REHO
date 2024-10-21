from reho.model.reho import *
from reho.plotting import plotting

if __name__ == '__main__':

    # Set building parameters
    # you can as well define your district from a csv file instead of reading the database
    reader = QBuildingsReader()
    n_house = 1
    qbuildings_data = reader.read_csv(buildings_filename='/Users/eduardo/REHO_local/REHO-HeatingBits/REHO/Projects/HeatingBits/Data/EPFL_nb_1.csv', nb_buildings= n_house)
    #reader.establish_connection('Suisse')
    #qbuildings_data = reader.read_db(transformer=3216, egid=[280001550])
    # Select weather data
    cluster = {'Location': 'Pully', 'Attributes': ['I', 'T', 'W'], 'Periods': 10, 'PeriodDuration': 24}

    # Set scenario

    scenario = dict()
    scenario['Objective'] = 'GWP'
    scenario['name'] = 'gwp'
    scenario['exclude_units'] = ['HeatPump_Geothermal','HeatPump_Air','HeatPump_Lake','HeatPump_Anergy','HeatPump_DHN', 'ElectricalHeater_SH', 'ThermalSolar', 'Battery'] #'OIL_Boiler',  'NG_Boiler','HeatPump_Air', 'HeatPump_Lake''HeatPump_Anergy''DataHeatSH',

    #
    #
    scenario['enforce_units'] = ['BESS_IP'] #'HeatPump_Geothermal_district','DHN_out_district','Battery_district','PV_district',
    scenario["specific"] = ["enforce_PV_max"]

    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {"Cost_demand_cst": 0.08, "Cost_supply_cst": 0.20},
                                            "Heat": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002,  "GWP_supply_cst": 0.000}})  #'NaturalGas': {"Cost_demand_cst": 0.01, "Cost_supply_cst": 0.10},
                                                                                                                #"Data": {"Cost_demand_cst": 0.0001, "Cost_supply_cst": 0.0002}}


    units = infrastructure.initialize_units(scenario, grids, district_data= True)
    parameters = {'n_vehicles': np.array([0.0]), 'T_DHN_supply_cst': np.repeat(70.0, n_house),'T_DHN_return_cst': np.repeat(60.0, n_house),"TransformerCapacity": np.array([1e8, 0])}
    #parameters = {}

    # Set method options
    method = {'building-scale': True,'save_stream_t': True, 'use_dynamic_emission_profiles': True, 'save_streams': True, 'use_Storage_Interperiod': True} #, 'use_pv_orientation': True
    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver ='gurobi') #parameters=parameters,
    reho.single_optimization()
    #plotting.plot_composite_curve(reho.results["totex"][0], cluster, plot= True, periods =["Yearly"]) #,"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
    #plotting.yearly_demand_plot(reho.results["totex"][0], cluster, plot=True)
    # Save results
    filename='epfl_BAU'
    reho.save_results(format=['xlsx', 'pickle'], filename=filename)
    plotting.plot_performance(reho.results, plot='costs', indexed_on='Scn_ID', label='EN_long').show()
    plotting.plot_performance(reho.results, plot='gwp', indexed_on='Scn_ID', label='EN_long').show()
    plotting.plot_sankey(reho.results['gwp'][0], label='EN_long', color='ColorPastel').show()
    # Construct the full file path
    # plotting.yearly_demand_plot(filename)

    # path_egid_map =
    # Read typical day distribution and buildings profiles
