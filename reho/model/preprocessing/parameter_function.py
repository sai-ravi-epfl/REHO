import numpy as np

def generate_wastewater_profiles(ampl,cluster):

    nb_timesteps = cluster['Periods'] * cluster['PeriodDuration'] + 2
    wastewater = 0.9 *