from reho.model.reho import *
from reho.model.preprocessing.clustering import Clustering
from scripts.templates.switchLoad.afterClustering.data_heat_switch_init_after_clustering import *

if __name__ == '__main__':

    # Set building parameters
    # you can as well define your district from a csv file instead of reading the database
    reader = QBuildingsReader()
    n_house = 1
    qbuildings_data = reader.read_csv(buildings_filename='/scripts/template/data/EPFL_2.csv', nb_buildings= n_house)
    #reader.establish_connection('Suisse')
    #qbuildings_data = reader.read_db(transformer=3216, egid=[280001550])
    # Select weather data
    cluster = {'Location': 'Pully', 'Attributes': ['I', 'T','E','D'], 'Periods': 10, 'PeriodDuration': 24}
    attributes = ['Irr', 'Text', 'Weekday','DataLoad']
    weather_file = r'/scripts/template/data/profiles/pully.csv'
    weather.data_centre_profile(size = 288)
    df_annual = weather.read_custom_weather(weather_file)
    df_annual = df_annual[attributes]
    nb_clusters = [10]
    cl = Clustering(data=df_annual, nb_clusters=nb_clusters, option={"year-to-day": True, "extreme": []}, pd=24)
    cl.run_clustering()
    val_cls = weather.generate_output_data(cl, attributes, "Pully")
    data_centre_heat_profile = weather.data_centre_profiles(val_cls)

    # change data_centre_heat_profile which is a numpy.ndarray to .dat file
    path_to_data_centre_heat_profile = r'/scripts/template/data/clustering/data_centre_heat_profile.dat'
    np.savetxt(path_to_data_centre_heat_profile, data_centre_heat_profile, delimiter='\t')

    # manipulate data_center_heat_profile according to gwp
    path_to_data_centre_heat_profile_2 = r'/scripts/template/data/clustering/D_Pully_10_24_T_I_W_D.dat'
    load_profile = pd.read_csv(path_to_data_centre_heat_profile_2, sep='\t', header=None, engine='python')
    path_to_emissions = r'/reho/data/emissions/electricity_matrix_2019_reduced.csv'
    path_timestamp_dat = r'/scripts/template/data/clustering/timestamp_Pully_10_24_T_I_W_D.dat'
    model_path_gwp = r'/scripts/templates/switchLoad/data_heat_switch_after_clustering_gwp.mod'
    output_single_column_dat_path_GWP = r'/scripts/template/data/clustering/D_Pully_10_24_T_I_W_D_test.dat'

    total_gwp, shifted_load_df_GWP, gwp_profile, all_values_gwp = process_and_optimize_data_GWP(
        path_to_data_centre_heat_profile, path_to_emissions, path_timestamp_dat, model_path_gwp,
        output_single_column_dat_path_GWP)

    # take all_values_gwp and convert it to same form as data_centre_heat_profile which is 'numpy.ndarray'
    data_centre_heat_profile_2 = np.array(all_values_gwp)
    # print(data_centre_heat_profile_2)

    # add all values of data_centre_heat_profile_1 (numpy.ndarray) to one total value
    total_1 = np.sum(data_centre_heat_profile)
    print('length data_centre_heat_profile',len(data_centre_heat_profile))
    print('total_1', total_1)

    total_2 = np.sum(data_centre_heat_profile_2)
    print('total_2', total_2)

    # change laod profile to dataframe
    load_profile_df = pd.DataFrame(load_profile)
    load_profile = load_profile_df[0].values
    total_3 = np.sum(load_profile)
    print('length load_profile',len(load_profile))
    print('total_3', total_3)

    data_centre_heat_profile_1 = pd.read_csv(output_single_column_dat_path_GWP, sep='\t', header=None, engine='python')
    data_centre_heat_profile_1_df = pd.DataFrame(data_centre_heat_profile_1)
    data_centre_heat_profile_1 = data_centre_heat_profile_1_df[0].values
    total_4 = np.sum(data_centre_heat_profile_1)
    print('length load_profile',len(data_centre_heat_profile_1))
    print('total_4', total_4)

    # make subtraction of data_centre_heat_profile and D_Pully_10_24_T_I_W_D.dat and save in difference.dat
    difference = data_centre_heat_profile - data_centre_heat_profile_2
    path_to_difference = r'/scripts/template/data/clustering/difference.dat'
    np.savetxt(path_to_difference, difference, delimiter='\t')
    total_difference = np.sum(difference)
    print('total_difference', total_difference)


    difference_1 = data_centre_heat_profile - load_profile
    path_to_difference_1 = r'/scripts/template/data/clustering/difference_1.dat'
    np.savetxt(path_to_difference_1, difference_1, delimiter='\t')
    total_difference_1 = np.sum(difference_1)
    print('total_difference_1', total_difference_1)


