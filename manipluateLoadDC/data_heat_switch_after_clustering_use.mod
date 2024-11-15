######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Load change from data center
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

# load data
param T ;  # number of hours of all clusters (24 hours per cluster)
param load {1..T};  # original load profile datacentre after clustering
param objective {1..T};  # objective values after clustering

# variables
var shifted_load {1..T} >= 0;

# Constraints
s.t. max_shift {t in 1..T}:
    shifted_load[t] <= 288 * 0.62;  # [kW] must be smaller than maximum capacity of datacentre

s.t. min_shift {t in 1..T}:
    shifted_load[t] >= 0.7 * load[t];

# Define d as T/24
param d := T div 24;

s.t. total_load {day in 0..d-1}:  # d days
    sum {h in 1..24} shifted_load[day*24 + h] = sum {h in 1..24} load[day*24 + h];

# Objective
maximize use:
    sum {t in 1..T} shifted_load[t] * objective[t];

# load data
data;
end;
