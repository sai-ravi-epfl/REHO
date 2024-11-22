import pandas as pd

def extract_and_save_data(excel_file):
    # Definierte Parameter innerhalb der Funktion
    sheet_name = 'df_Buildings_t'
    column_name = 'Domestic_electricity'
    output_dat_file = '../switchLoad/electricity_demand_BAU_GWP.dat'

    # Load the Excel file
    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols=[column_name])

    # Extract the data from the column
    heating_data = df[column_name].tolist()

    # Write the data to a .dat file
    with open(output_dat_file, 'w') as f:
        for value in heating_data:
            f.write(f"{value}\n")

# Beispielaufruf der Funktion
path_tp_excel_file_BAU = r'/scripts/template/results/ALL_EPFL_BAU_gwp.xlsx'
extract_and_save_data(path_tp_excel_file_BAU)

