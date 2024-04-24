from reho.model.reho import *
from reho.plotting import plotting

if __name__ == '__main__':

    # Set building parameters
    # you can as well define your district from a csv file instead of reading the database
    reader = QBuildingsReader()
    qbuildings_data = reader.read_csv(buildings_filename='C:/Users/ravi/Desktop/REHO/scripts/template/data/EPFL_2.csv', nb_buildings=60000)

    # Select weather data
    cluster = {'Location': 'Pully', 'Attributes': ['I', 'T', 'W', 'E'], 'Periods': 10, 'PeriodDuration': 24}

    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'
    scenario['exclude_units'] = ['Battery', 'NG_Cogeneration', 'Air_Conditioner_Air']
    scenario['enforce_units'] = []

    # Initialize available units and grids
    grids = infrastructure.initialize_grids()
    units = infrastructure.initialize_units(scenario, grids)

    # Set method options
    method = {'building-scale': True,'save_stream_t': True}
    # Run optimization
    reho = reho(qbuildings_data=qbuildings_data, units=units, grids=grids, cluster=cluster, scenario=scenario, method=method, solver="gurobi")
    reho.single_optimization()
    plotting.plot_composite_curve(reho.results["totex"][0] , cluster, plot= True, periods =["January", "February", "March", "April", "May", "June", "July", "August",
             "September", "October", "November", "December"])
    # Save results
    reho.save_results(format=['xlsx', 'pickle'], filename='3a')
