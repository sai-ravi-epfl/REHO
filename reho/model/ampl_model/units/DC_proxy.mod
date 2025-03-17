######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Heat recovery from data center
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

param DC_efficiency{u in UnitsOfType['DataHeat']} default 0.96;
param DC_partload_max{u in UnitsOfType['DataHeat']} default 1;

# Data flow processed
subject to DC_data{h in House, u in UnitsOfType['DataHeat'] inter UnitsOfHouse[h], p in Period, t in Time[p]}:
Units_supply['Data',u,p,t] = Units_demand['Electricity',u,p,t];

subject to DC_energy_balance{h in House,u in UnitsOfType['DataHeat'] inter UnitsOfHouse[h],p in Period,t in Time[p]}:
sum{st in StreamsOfUnit[u],se in ServicesOfStream[st]} Streams_Q[se,st,p,t] = DC_efficiency[u]*Units_demand['Electricity',u,p,t];

subject to DC_c1{h in House,u in UnitsOfType['DataHeat'] inter UnitsOfHouse[h],p in Period,t in Time[p]}:
sum{st in StreamsOfUnit[u],se in ServicesOfStream[st]} Streams_Q[se,st,p,t] <= Units_Mult[u]*DC_partload_max[u];


param DH_efficiency{u in UnitsOfType['DataHeat']} default 0.96;		# 90-96% of energy is recovered from server
param DC_heat_recovery{u in UnitsOfType['DataHeat']} default 1;


# ---------------------------------------- CONSTRAINTS ---------------------------------------

# Data flow processed
subject to DH_d1{ u in UnitsOfType['DataHeat'], p in Period, t in Time[p]}:
        Units_supply['Data',u,p,t] = 1.3*Units_demand['Electricity',u,p,t];

#subject to DH_d2{ u in UnitsOfType['DataHeat'], p in Period, t in Time[p]}:
#       Units_demand['Electricity',u,p,t] = data_EUD['Data',p,t];


# Heat produced from electricity (thermal output = electrical input * DH_thermal_efficiency)
subject to DH_EB_c1{u in UnitsOfType['DataHeat'] ,p in Period,t in Time[p]}:
        Units_supply['Heat',u,p,t] = DC_heat_recovery[u]*DH_efficiency[u]*Units_demand['Electricity',u,p,t]; #*elec_demand_datacentre['Electricity',p,t]; #kW


subject to DH_c1{u in UnitsOfType['DataHeat'],p in Period,t in Time[p]}:
        Units_supply['Data',u,p,t]<= 0.327*Units_Mult[u];

