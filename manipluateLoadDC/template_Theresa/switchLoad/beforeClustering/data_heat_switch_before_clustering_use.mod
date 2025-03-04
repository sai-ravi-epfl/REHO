######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Load change from data center
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

# load data
param T := 8760 ;  # Total number of hours per year
param load {1..T};  # Original load profile of the data center after clustering
param objective {1..T};  # Objective values after clustering
param size ;  # Size of the data center

# variables
var shifted_load {1..T} >= 0;  # Shifted load values, must be non-negative

# Constraints
s.t. max_shift {t in 1..T}:
    shifted_load[t] <= size * 0.62;  # [kW] Must be smaller than the maximum capacity of the data center

s.t. min_shift {t in 1..T}:
    shifted_load[t] >= 0.7 * load[t];  # Maximum 30% of the load can be shifted

# Define d as T/24
param d := T div 24;  # Number of days

s.t. total_load {day in 0..d-1}:  # d days
    sum {h in 1..24} shifted_load[day*24 + h] = sum {h in 1..24} load[day*24 + h];  # Total load must remain the same for each day

# Objective
maximize use:
    sum {t in 1..T} shifted_load[t] * objective[t];  # Maximize the use based on the shifted load and objective values

# load data
data;
end;