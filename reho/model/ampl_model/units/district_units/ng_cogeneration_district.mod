######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Natural gas cogeneration (district)
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Natural gas generator (district-level, keeping same unit type 'NG_Cogeneration')
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

param NG_Cogeneration_partload_max{u in UnitsOfType['NG_Cogeneration']} default 1;
param NG_Cogeneration_partload_min{u in UnitsOfType['NG_Cogeneration']} default 0.5;
param NG_Cogeneration_E_efficiency_nom{u in UnitsOfType['NG_Cogeneration']} default 0.40;
param NG_Cogeneration_Q_efficiency_nom{u in UnitsOfType['NG_Cogeneration']} default 0;

subject to NG_Cogeneration_c1{u in UnitsOfType['NG_Cogeneration'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t]= NG_Cogeneration_E_efficiency_nom[u]*Units_demand['NaturalGas',u,p,t];

subject to NG_Cogeneration_c2{u in UnitsOfType['NG_Cogeneration'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t]<=Units_Mult[u]*NG_Cogeneration_partload_max[u];

subject to NG_Cogeneration_c3{u in UnitsOfType['NG_Cogeneration'], p in Period, t in Time[p]}:
Units_supply['Electricity',u,p,t]>=Units_Mult[u]*NG_Cogeneration_partload_min[u];

