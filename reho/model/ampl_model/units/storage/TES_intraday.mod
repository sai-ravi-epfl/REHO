#####################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Intraday thermal energy storage
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

param ITES_eff_ch{u in UnitsOfType['DHN_tank']} 	default 0.9;		#-	[1]
param ITES_eff_di{u in UnitsOfType['DHN_tank']} 	default 0.9;
param ITES_limit_ch{u in UnitsOfType['DHN_tank']} default 0.8;			#-	[2] max charging limit
param ITES_limit_di{u in UnitsOfType['DHN_tank']} default 0.2;			#-	[1] max discharging limit
param ITES_efficiency{u in UnitsOfType['DHN_tank']} default 0.99997;

var ITES_E_stored{u in UnitsOfType['DHN_tank'],p in Period,t in Time[p]} >= 0;

#--Hourly Energy balance (valid for intra-period storage)
subject to ITES_energy_balance{u in UnitsOfType['DHN_tank'], p in Period,t in Time[p] diff {last(Time[p])}}:
(ITES_E_stored[u,p,next(t,Time[p])] - ITES_efficiency[u]*ITES_E_stored[u,p,t]) = 
	( ITES_eff_ch[u]*Units_demand['Heat',u,p,t] - (1/ITES_eff_di[u])*Units_supply['Heat',u,p,t] )*dt[p];



#--SoC constraints
subject to ITES_c1{u in UnitsOfType['DHN_tank'], p in Period,t in Time[p]}:
ITES_E_stored[u,p,t] <= ITES_limit_ch[u]*Units_Mult[u];

subject to ITES_c2{u in UnitsOfType['DHN_tank'], p in Period,t in Time[p]}:
ITES_E_stored[u,p,t] >= ITES_limit_di[u]*Units_Mult[u];


subject to ITES_c3{u in UnitsOfType['DHN_tank'] ,p in Period,t in Time[p]}:
Units_demand['Heat',u,p,t]*dt[p] <= (ITES_limit_ch[u]-ITES_limit_di[u])*Units_Mult[u];

subject to ITES_c4{u in UnitsOfType['DHN_tank'],p in Period,t in Time[p]}:
Units_supply['Heat',u,p,t]*dt[p] <= (ITES_limit_ch[u]-ITES_limit_di[u])*Units_Mult[u];

#--Cyclic
subject to ITES_E_stored_cyclic{u in UnitsOfType['DHN_tank'],p in Period}:
(ITES_E_stored[u,p,first(Time[p])] - ITES_efficiency[u]*ITES_E_stored[u,p,last(Time[p])]) = (ITES_eff_ch[u]*Units_demand['Heat',u,p,last(Time[p])] - (1/ITES_eff_di[u])*Units_supply['Heat',u,p,last(Time[p])])*dt[p];

