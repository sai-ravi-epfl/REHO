######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Natural gas generator (on-site electricity production only)
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

param NG_Generator_partload_max{u in UnitsOfType['NG_Generator']} default 1;
param NG_Generator_partload_min{u in UnitsOfType['NG_Generator']} default 0.3;
param NG_Generator_E_efficiency_nom{u in UnitsOfType['NG_Generator']} default 0.40;

subject to NG_Generator_energy_balance{ u in UnitsOfType['NG_Generator'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t] = NG_Generator_E_efficiency_nom[u]*Units_demand['NaturalGas',u,p,t];

subject to NG_Generator_c1{ u in UnitsOfType['NG_Generator'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t] <= Units_Mult[u]*NG_Generator_partload_max[u];

subject to NG_Generator_c2{ u in UnitsOfType['NG_Generator'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t] >= Units_Mult[u]*NG_Generator_partload_min[u];
