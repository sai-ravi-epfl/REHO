from reho.model.reho import *


if __name__ == '__main__':

    # Set building parameters
    reader = QBuildingsReader()
    reader.establish_connection('Geneva')
    qbuildings_data = reader.read_db(234, nb_buildings=2)

    # Select clustering options for weather data
    cluster = {'Location': 'Geneva', 'Attributes': ['T', 'I', 'E', 'CS'], 'Periods': 10, 'PeriodDuration': 24, 'custom_weather': '/Users/ravi/Desktop/PhD/My_Reho_Qgis_files/Reho_Sai_Fork/scripts/examples/data/profiles/Sion.csv'}

    # Set scenario
    scenario = dict()
    scenario['Objective'] = ['GWP', 'CAPEX']
    scenario['nPareto'] = 2
    scenario['name'] = 'pareto'
    scenario['exclude_units'] = ['NG_Cogeneration', 'OIL_Boiler']
    scenario['enforce_units'] = ['Battery_district']

    # Initialize available units and grids
    grids = infrastructure.initialize_grids()
    units = infrastructure.initialize_units(scenario, grids, district_data= True)

    # Set method options
    method = {'district-scale': True, 'use_dynamic_emissions_profile': True}
    DW_params = {'max_iter': 2}

    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units, grids=grids, cluster=cluster, scenario=scenario, method=method, DW_params=DW_params, solver="gurobi")
    reho.generate_pareto_curve()

    # Save results
    reho.save_results(format=[ 'pickle', 'xlsx'], filename='2b') #'xlsx',
