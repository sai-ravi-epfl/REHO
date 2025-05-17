######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Natural gas generator (on-site electricity production only)
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

param NG_Generator_partload_max{u in UnitsOfType['NG_Generator_district']} default 1;
param NG_Generator_E_efficiency_nom{u in UnitsOfType['NG_Generator_district']} default 0.90;

subject to NG_Generator_energy_balance{ u in UnitsOfType['NG_Generator_district'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t] = NG_Generator_E_efficiency_nom[u]*Units_demand['NaturalGas',u,p,t];

subject to NG_Generator_c1{ u in UnitsOfType['NG_Generator_district'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t] <= Units_Mult[u]*NG_Generator_partload_max[u];

subject to Link_DC_to_district_NG{u in UnitsOfType['NG_Generator_district'], v in UnitsOfType['DataHeat'], p in Period,t in Time[p]}:
Units_supply['Electricity', u,p,t] <= Units_demand['Electricity', v,p,t]