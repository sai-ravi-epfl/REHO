######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Load change from data center
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

# load data
param T ;  # Number of hours of all clusters (24 hours per cluster)
param load {1..T};  # Original load profile of the data center after clustering
param objective {1..T};  # Objective values after clustering

# variables
var shifted_load {1..T} >= 0;  # Shifted load values, must be non-negative

# Constraints
s.t. max_shift {t in 1..T}:
    shifted_load[t] <= 288 * 0.62;  # [kW] Must be smaller than the maximum capacity of the data center

s.t. min_shift {t in 1..T}:
    shifted_load[t] >= 0.7 * load[t];  # Maximum 30% of the load can be shifted

# Define d as T/120
param d := T div 120;  # Number of periods, each period is 120 hours (5 days)

s.t. total_load {period in 0..d-1}:  # d periods of 5 days
    sum {h in 1..120} shifted_load[period*120 + h] = sum {h in 1..120} load[period*120 + h];  # Total load must remain the same for each period

# Objective
minimize gwp:
    sum {t in 1..T} shifted_load[t] * objective[t];  # Minimize the global warming potential (GWP) based on the shifted load and objective values

# load data
data;
end;
