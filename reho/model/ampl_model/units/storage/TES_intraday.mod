#####################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Intraday thermal energy storage
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################


param ITES_limit_ch{u in UnitsOfType['DHN_tank']} default 1;			#-	[2] max charging limit
param ITES_limit_di{u in UnitsOfType['DHN_tank']} default 0;			#-	[1] max discharging limit
param ITES_self_discharge{u in UnitsOfType['DHN_tank']} default 0.9999729;	#-	[1]
param ITES_efficiency{u in UnitsOfType['DHN_tank']} default 0.97128;
var ITES_E_stored{u in UnitsOfType['DHN_tank'],p in Period,t in Time[p]} >= 0;

var mode_charge_ITES{u in UnitsOfType['DHN_tank'], p in Period, t in Time[p]} binary := 0;
var mode_discharge_ITES{u in UnitsOfType['DHN_tank'], p in Period, t in Time[p]} binary := 0;
param ITES_mode := 1e6;

#--Hourly Energy balance (valid for intra-period storage)
subject to ITES_energy_balance{u in UnitsOfType['DHN_tank'], p in Period,t in Time[p] diff {last(Time[p])}}:
(ITES_E_stored[u,p,next(t,Time[p])] - ITES_self_discharge[u]*ITES_E_stored[u,p,t]) =
	(ITES_efficiency[u]*Units_demand['Heat',u,p,t]
	- (1/ITES_efficiency[u])*Units_supply['Heat',u,p,t] )*dt[p];

#--SoC constraints
subject to ITES_c1{u in UnitsOfType['DHN_tank'], p in Period,t in Time[p]}:
ITES_E_stored[u,p,t] <= ITES_limit_ch[u]*Units_Mult[u];

subject to ITES_c2{u in UnitsOfType['DHN_tank'], p in Period,t in Time[p]}:
ITES_E_stored[u,p,t] >= ITES_limit_di[u]*Units_Mult[u];

#--Cyclic
subject to ITES_E_stored_cyclic{u in UnitsOfType['DHN_tank'],p in Period}:
 ITES_E_stored[u,p,first(Time[p])] = ITES_self_discharge[u]*ITES_E_stored[u,p,last(Time[p])] +(ITES_efficiency[u]*Units_demand['Heat',u,p,last(Time[p])] - (1/ITES_efficiency[u])*Units_supply['Heat',u,p,last(Time[p])])*dt[p];


param delta_T_ITES{u in UnitsOfType['DHN_tank']} default 60;


# constraint to impose the minimum allowed temperature inside the storage
subject to min_T_allowed{u in UnitsOfType['DHN_tank'], p in Period,t in Time[p]}:
	Units_Mult[u]*Text_Geneva[p,t]+ITES_E_stored_IP[u,p,t]*delta_T_ITES[u] >= Units_Mult[u]*22.5;
