from reho.model.reho import *
from reho.plotting import plotting

if __name__ == '__main__':

    # Set building parameters
    reader = QBuildingsReader()
    reader.establish_connection('Suisse')
    qbuildings_data = reader.read_db(transformer=10889, nb_buildings=4)

    # Select weather data
    cluster = {'Location': 'Geneva', 'Attributes': ['T', 'I', 'W'], 'Periods': 10, 'PeriodDuration': 24}

    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'
    scenario['exclude_units'] = ['Battery', 'NG_Cogeneration']
    scenario['enforce_units'] = ['HeatPump_DHN']
    scenario["specific"] = ["enforce_DHN"]
    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {},
                                             'NaturalGas': {},
                                             'Heat': {'Cost_supply_cst = 0.05'}})
    units = infrastructure.initialize_units(scenario, grids, district_data=True)

    # Set method options
    # you can specify if the DHN is based on CO2. If not, a water DHN is assumed
    method = {'building-scale': True, 'DHN_CO2': True}

    # Set specific parameters
    # specify the temperature of the DHN
    parameters = {'T_DHN_supply_cst': np.repeat(20.0, 4), "T_DHN_return_cst": np.repeat(15.0, 4), "TransformerCapacity": np.array([1e6,10,1e6])}
    parameters_1 = {'T_DHN_supply_cst': np.repeat(20.0, 4), "T_DHN_return_cst": np.repeat(15.0, 4), "TransformerCapacity": np.array([1e6,5,1e6])}
    parameters_3 = {'T_DHN_supply_cst': np.repeat(20.0, 4), "T_DHN_return_cst": np.repeat(15.0, 4), "TransformerCapacity": np.array([1e6,2,1e6])}
    # Run optimization
    reho0 = reho(qbuildings_data=qbuildings_data, units=units, grids=grids, parameters=parameters, cluster=cluster,scenario=scenario, method=method, solver="gurobi")
    reho1 = reho(qbuildings_data=qbuildings_data, units=units, grids=grids, parameters=parameters_1, cluster=cluster,scenario=scenario, method=method, solver="gurobi")
    reho2 = reho(qbuildings_data=qbuildings_data, units=units, grids=grids, parameters=parameters_3, cluster=cluster,scenario=scenario, method=method, solver="gurobi")
    reho0.get_DHN_costs()
    reho1.get_DHN_costs()
    reho2.get_DHN_costs()# run one optimization forcing DHN to find costs DHN connection per house
    reho0.single_optimization()  # run optimization with DHN costs
    reho1.single_optimization()
    reho2.single_optimization()
    # Save results
    reho0.save_results(format=['xlsx', 'pickle'], filename='3g')
    reho1.save_results(format=['xlsx', 'pickle'], filename='3g_5kw')
    reho2.save_results(format=['xlsx', 'pickle'], filename='3g_2kW')

    # Plot results
    plotting.plot_performance(reho0.results, plot='costs').show()
    plotting.plot_sankey(reho.results["totex"][0]).show()

    plotting.plot_performance(reho1.results, plot='costs').show()
    plotting.plot_sankey(reho1.results["totex"][0]).show()

    plotting.plot_performance(reho2.results, plot='costs').show()
    plotting.plot_sankey(reho2.results["totex"][0]).show()
