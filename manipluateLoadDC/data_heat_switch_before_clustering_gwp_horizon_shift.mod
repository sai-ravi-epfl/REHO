######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Load change from data center
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

# load data
param T := 8760 ;  # total number of hours per year
param load {1..T};  # original load profile datacentre after clustering
param objective {1..T};  # objective values after clustering
param size ;  # size of datacentre

# variables
var shifted_load {1..T} >= 0;

# Constraints
s.t. max_shift {t in 1..T}:
    shifted_load[t] <= size * 0.62;  # [kW] must be smaller than maximum capacity of datacentre

s.t. min_shift {t in 1..T}:
    shifted_load[t] >= 0.5 * load[t]; # max 50% shiftable

# Define d as T/24
param d := T div 24;

s.t. total_load {day in 0..d-1}:  # d days
    sum {h in 1..24} shifted_load[day*24 + h] = sum {h in 1..24} load[day*24 + h];

# Objective
minimize gwp:
    sum {t in 1..T} shifted_load[t] * objective[t];

# load data
data;
end;
