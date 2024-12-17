#####################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Seasonal thermal energy storage
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################


param STES_limit_ch_IP{u in UnitsOfType['STES']} default 0.8;			#-	[2]
param STES_limit_di_IP{u in UnitsOfType['STES']} default 0.2;			#-	[1]
param S_rate_IP{u in UnitsOfType['STES']} default 1;					#-
param STES_self_discharge_IP{u in UnitsOfType['STES']} default 0.99999;	#-	[1]
param STES_efficiency_IP{u in UnitsOfType['STES']} default 0.999;
param STES_initial_SOC{u in UnitsOfType['STES']} default 0.5;  # Initial SOC as a fraction of capacity
param STES_max_SOC{u in UnitsOfType['STES']} default 0.8; 
param rate_limit{u in UnitsOfType['STES']} default 0.1; 
var STES_E_stored_IP{u in UnitsOfType['STES'], hy in Year} >= 0;

#--Hourly Energy balance (valid for inter-period storage)
subject to STES_energy_balance_IP{u in UnitsOfType['STES'], hy in Year}:
(STES_E_stored_IP[u,next(hy,Year)] - STES_self_discharge_IP[u]*STES_E_stored_IP[u,hy]) = 
	(STES_efficiency_IP[u]*Units_demand['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]]
	- (1/STES_efficiency_IP[u])*Units_supply['Heat',u,PeriodOfYear[hy],TimeOfYear[hy]] )*dt[PeriodOfYear[hy]];


subject to STES_rate_smoothing{u in UnitsOfType['STES'], p in Period, t in Time[p] diff {last(Time[p])}}:
abs(STES_E_stored_IP[u, p, t+1] - STES_E_stored_IP[u, p, t]) <= rate_limit[u] * Units_Mult[u];

#--SoC constraints
subject to STES_c1_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] <= STES_limit_ch_IP[u]*Units_Mult[u];

subject to STES_c2_IP{u in UnitsOfType['STES'], hy in Year}:
STES_E_stored_IP[u,hy] >= STES_limit_di_IP[u]*Units_Mult[u];

#-- Power constraints
subject to STES_c3_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_demand['Heat',u,p,t]*dt[p] <= (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u]*S_rate_IP[u];

subject to STES_c4_IP{u in UnitsOfType['STES'],p in Period,t in Time[p]}:
Units_supply['Heat',u,p,t]*dt[p] <= (STES_limit_ch_IP[u]-STES_limit_di_IP[u])*Units_Mult[u]*S_rate_IP[u];












