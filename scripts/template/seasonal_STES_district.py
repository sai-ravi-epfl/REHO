from reho.model.reho import *
from reho.plotting import plotting
import numpy as np


if __name__ == '__main__':

    # Set building parameters
    reader = QBuildingsReader()
    reader.establish_connection('Geneva')
    qbuildings_data = reader.read_db(transformer=234, egid=['1017073/1017074', '1017109']) #, '1017079', '1030377/1030380'

    # Select clustering options for weather data
    cluster = {'Location': 'Geneva', 'Attributes': ['T', 'I', 'W'], 'Periods': 10, 'PeriodDuration': 24}

    file_name = 'C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/waste_heat.csv'
    waste_heat = np.loadtxt(file_name)

    file_name1 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/STC_Tml_district1.csv'
    STC_Tml_district = np.loadtxt(file_name1)

    file_name2 ='C:/Users/ettor/Desktop/REHO/reho/data/infrastructure/Irr_Geneva.csv'
    Irr_Geneva = np.loadtxt(file_name2)

    # Set scenario
    scenario = dict()
    scenario['Objective'] = 'TOTEX'
    scenario['name'] = 'totex'
    scenario['exclude_units'] = ['NG_Boiler','NG_Boiler_district','Heat_pump','BESS_IP','NG_Cogeneration_district','ThermalSolar_district']  #,'ThermalSolar_district'
    scenario["specific"] = ["enforce_DHN"]
    scenario['enforce_units'] = ['BESS_IP_district','STES_district']
    # Initialize available units and grids
    grids = infrastructure.initialize_grids({'Electricity': {},
                                             'NaturalGas': {},
                                             'Heat': {}})

    units = infrastructure.initialize_units(scenario, grids, district_data = True, storage_data= True) #, storage_data= True  ,'use_Storage_Interperiod': True
    parameters = {'TransformerCapacity_heat_t': waste_heat, 'STC_Tml_district':STC_Tml_district, 'I_global_STC':Irr_Geneva}  #, 'STC_Tlm_district':STC_Tml_district, 'I_global_STC':Irr_Geneva

    # Set method options
    method = {'building-scale': True, 'use_storage_interperiod':True}



    # Run optimization
    reho = REHO(qbuildings_data=qbuildings_data, units=units,parameters=parameters, grids=grids, cluster=cluster, scenario=scenario, method=method, solver="gurobi")
    reho.single_optimization()

    # Save results
    reho.save_results(format=['xlsx', 'pickle'], filename='0')
