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
    shifted_load[t] >= 0.7 * load[t]; # max 30% shiftable

# Define d as T/120
param d := T div 168;

s.t. total_load {period in 0..d-1}:  # d periods of 5 days
    sum {h in 1..168} shifted_load[period*168 + h] = sum {h in 1..168} load[period*168 + h];

# Objective
minimize gwp:
    sum {t in 1..T} shifted_load[t] * objective[t];

# load data
data;
end;;
