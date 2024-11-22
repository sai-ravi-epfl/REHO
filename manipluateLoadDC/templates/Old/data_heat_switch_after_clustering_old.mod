######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Load change from data center
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

# load data
param T ;  # number of hours of all clusters(24 hours per cluster)
param load {1..T};  # original load profile datacentre after clustering
param gwp {1..T};  # GWP values after clustering


# variables
var shifted_load {1..T} >= 0;

# Constraints
s.t. max_shift {t in 1..T}:
    shifted_load[t] <= 288*0.62;  # [kW] must be smaller than maximum capacity of datacentre

s.t. min_shift {t in 1..T}:
    shifted_load[t] >= 0.7 * load[t];

s.t. total_load {d in 0..9}:  # 10 days
    sum {h in 1..24} shifted_load[d*24 + h] = sum {h in 1..24} load[d*24 + h];

# objective
minimize total_gwp:
    sum {t in 1..T} shifted_load[t] * gwp[t];

# load data
data;
end;
