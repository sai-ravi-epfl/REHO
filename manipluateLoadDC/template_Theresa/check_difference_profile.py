# Compare two CSV files for equality. Input: file paths.
# Output: True if files are identical, False otherwise.

import pandas as pd

def compare_profiles(file1, file2):
    # Lade die Profile
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Vergleiche die Profile
    comparison = df1.equals(df2)

    return comparison


# Dateipfade zu den Profilen
file1 = r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\reconstructed_year_16clusters.csv'
file2 = r'C:\Users\there\Desktop\REHO2\scripts\template_Sai\reconstructed_year_16clusters_new.csv'

# Vergleiche die Profile und gib das Ergebnis aus
result = compare_profiles(file1, file2)
print(f"Die Profile sind {'identisch' if result else 'unterschiedlich'}.")