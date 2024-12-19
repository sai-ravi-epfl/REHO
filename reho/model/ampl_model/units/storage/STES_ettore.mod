#####################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Sensible heat seasonal thermal energy storage
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################


param STES_limit_ch_IP{u in UnitsOfType['STES']} default 1;			#-	[2] max charging limit
param STES_limit_di_IP{u in UnitsOfType['STES']} default 0;			#-	[1] max discharging limit
param STES_self_discharge_IP{u in UnitsOfType['STES']} default 0.9999729;	#-	[1]
param STES_efficiency_IP{u in UnitsOfType['STES']} default 0.97128;
var STES_E_stored_IP{u in UnitsOfType['STES'], hy in Year} >= 0;

var mode_charge_STES{u in UnitsOfType['STES'], p in Period, t in Time[p]} binary := 0;
var mode_discharge_STES{u in UnitsOfType['STES'], p in Period, t in Time[p]} binary := 0;
param STES_mode := 1e6;

#--Hourly Energy balance (valid for inter-period storage)
subject to STES_energy_balance_IP{u in UnitsOfType['STES'], hy in Year}:
(STES_E_stored_IP[u,next(hy,Year)] - STES_self_discharge_IP[u]*STES_E_stored_IP[u,hy]) = 
	(STES_efficiency_IP[u]*Units_demand['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]]
	- (1/STES_efficiency_IP[u])*Units_supply['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]])*dt[PeriodOfYear[hy]];

#--SoC constraints
subject to STES_c1_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] <= STES_limit_ch_IP[u]*Units_Mult[u];

subject to STES_c2_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] >= STES_limit_di_IP[u]*Units_Mult[u];



# never charge and discharge storage simultaneously:
subject to is_stor_STES_discharging{u in UnitsOfType['STES'], p in Period, t in Time[p]}:
    Units_supply['Heat',u,p,t] <= mode_discharge_STES[u,p,t] * STES_mode;

subject to is_stor_STES_charging{u in UnitsOfType['STES'], p in Period, t in Time[p]}:
    Units_demand['Heat',u,p,t] <= mode_charge_STES[u,p,t] * STES_mode;

subject to no_charg_discharg_STES{u in UnitsOfType['STES'], p in Period, t in Time[p]}:
    mode_discharge_STES[u,p,t] + mode_charge_STES[u,p,t] <= 1;

subject to combine{ui in UnitsOfType['STES'],uj in UnitsOfType['ThermalSolar_district'], p in Period, t in Time[p]}:
	Units_demand['Heat',ui,p,t] = Units_supply['Heat',uj,p,t];

/*
subject to STES_c3_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_demand['Heat',u,p,t]*dt[p] <= STES_mode[u,p,t] * (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u];

subject to STES_c4_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_supply['Heat',u,p,t]*dt[p] <= (1-STES_mode[u,p,t]) * (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u];
*/


#--Cyclic
subject to STES_E_stored_IP_cyclic{u in UnitsOfType['STES']}:
STES_E_stored_IP[u,first(Year)] = STES_self_discharge_IP[u]*STES_E_stored_IP[u,last(Year)] +
	(0.792*Units_demand['Heat',u,PeriodOfYear[last(Year)],TimeOfYear[last(Year)]] - (1/0.593)*Units_supply['Heat',u,PeriodOfYear[last(Year)],TimeOfYear[last(Year)]])*dt[PeriodOfYear[last(Year)]];


#####################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Latent heat seasonal thermal storage
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################




/*
param STES_limit_ch_IP{u in UnitsOfType['STES']} default 0.8;			#-	[2] max charging limit
param STES_limit_di_IP{u in UnitsOfType['STES']} default 0.2;			#-	[1] max discharging limit
param STES_self_discharge_IP{u in UnitsOfType['STES']} default 0.9999854;	#-	[1]
param STES_efficiency_ch_IP{u in UnitsOfType['STES']} default 0.91;
param STES_efficiency_di_IP{u in UnitsOfType['STES']} default 0.87;
var STES_E_stored_IP{u in UnitsOfType['STES'], hy in Year} >= 0;
var STES_mode{u in UnitsOfType['STES'], p in Period, t in Time[p]} binary;

#--Hourly Energy balance (valid for inter-period storage)
subject to STES_energy_balance_IP{u in UnitsOfType['STES'], hy in Year}:
(STES_E_stored_IP[u,next(hy,Year)] - STES_self_discharge_IP[u]*STES_E_stored_IP[u,hy]) = 
	(STES_efficiency_ch_IP[u]*Units_demand['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]]
	- (1/STES_efficiency_di_IP[u])*Units_supply['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]] )*dt[PeriodOfYear[hy]];

#--SoC constraints
subject to STES_c1_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] <= STES_limit_ch_IP[u]*Units_Mult[u];

subject to STES_c2_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] >= STES_limit_di_IP[u]*Units_Mult[u];

subject to STES_c3_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_demand['Heat',u,p,t]*dt[p] <= STES_mode[u,p,t] * (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u];

subject to STES_c4_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_supply['Heat',u,p,t]*dt[p] <= (1-STES_mode[u,p,t]) * (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u];


*/

#####################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Adsorption seasonal thermal storage
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################




/*
param STES_limit_ch_IP{u in UnitsOfType['STES']} default 0.8;			#-	[2] max charging limit
param STES_limit_di_IP{u in UnitsOfType['STES']} default 0.2;			#-	[1] max discharging limit
param STES_self_discharge_IP{u in UnitsOfType['STES']} default 1;	#-	[1]
param STES_efficiency_ch_IP{u in UnitsOfType['STES']} default 0.792;
param STES_efficiency_di_IP{u in UnitsOfType['STES']} default 0.593;
var STES_E_stored_IP{u in UnitsOfType['STES'], hy in Year} >= 0;
var STES_mode{u in UnitsOfType['STES'], p in Period, t in Time[p]} binary;

#--Hourly Energy balance (valid for inter-period storage)
subject to STES_energy_balance_IP{u in UnitsOfType['STES'], hy in Year}:
(STES_E_stored_IP[u,next(hy,Year)] - STES_self_discharge_IP[u]*STES_E_stored_IP[u,hy]) = 
	(STES_efficiency_ch_IP[u]*Units_demand['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]]
	- (1/STES_efficiency_di_IP[u])*Units_supply['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]] )*dt[PeriodOfYear[hy]];

#--SoC constraints
subject to STES_c1_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] <= STES_limit_ch_IP[u]*Units_Mult[u];

subject to STES_c2_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] >= STES_limit_di_IP[u]*Units_Mult[u];

subject to STES_c3_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_demand['Heat',u,p,t]*dt[p] <= STES_mode[u,p,t] * (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u];

subject to STES_c4_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_supply['Heat',u,p,t]*dt[p] <= (1-STES_mode[u,p,t]) * (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u];


*/




