######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
#---TAP WATER MODEL
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################
#-Static natural gas - fired boiler model including:
#	1. part-load efficiency
# ----------------------------------------- PARAMETERS ---------------------------------------
param fresh_water_demand{h in House,p in Period,t in Time[p]} default 100; #l/h

subject to fresh_constraint_1{h in House,u in UnitsOfType['tap_water'] inter UnitsOfHouse[h],p in Period,t in Time[p]}:
fresh_water_demand[h,p,t] = Units_demand['fresh_water',u,p,t];


subject to fresh_constraint_2{u in UnitsOfType['tap_water'],p in Period,t in Time[p]}:
Units_demand['fresh_water',u,p,t] <= Units_Mult[u];

