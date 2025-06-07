import os
import pickle

def load_pickle(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

def combine_pickles(folder_path):
    combined_data = {'gwp': {}}
    pareto_id = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.pickle'):
            filepath = os.path.join(folder_path, filename)
            data = load_pickle(filepath)
            for key, value in data['gwp'].items():
                combined_data['gwp'][pareto_id] = value
                pareto_id += 1

    return combined_data

def save_combined_pickle(data, output_pickle_path):
    with open(output_pickle_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"Combined data saved as pickle file: {output_pickle_path}")

# Path to the folder containing the pickle files
folder_path = r"C:\Users\there\Downloads\results_DC_PV\grid_non_shifted"

# Combine the pickle files in the folder
combined_data = combine_pickles(folder_path)

# Save the combined data as a new pickle file
output_pickle_path = r'C:\Users\there\Downloads\results_DC_PV\grid_non_shifted.pickle'
save_combined_pickle(combined_data, output_pickle_path)