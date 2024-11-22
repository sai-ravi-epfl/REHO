import pandas as pd

def extract_and_save_data(excel_file):
    # Definierte Parameter innerhalb der Funktion
    sheet_name = 'df_Buildings_t'
    column_name_heating = 'House_Q_heating'
    column_name_electricity = 'Domestic_electricity'
    output_dat_file_heating = '../switchLoad/space_heating_BAU_GWP.dat'
    output_dat_file_electricity = '../switchLoad/electricity_demand_BAU_GWP.dat'

    # Load the Excel file with both columns
    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=[column_name_heating, column_name_electricity])

    # Extract the data from the columns
    heating_data = df[column_name_heating].tolist()
    electricity_data = df[column_name_electricity].tolist()

    # Write the data to .dat files
    with open(output_dat_file_heating, 'w') as f:
        for value in heating_data:
            f.write(f"{value}\n")
    with open(output_dat_file_electricity, 'w') as f:
        for value in electricity_data:
            f.write(f"{value}\n")

# Beispielaufruf der Funktion
path_to_excel_file_BAU = r'/scripts/template/results/ALL_EPFL_BAU_gwp.xlsx'
extract_and_save_data(path_to_excel_file_BAU)
