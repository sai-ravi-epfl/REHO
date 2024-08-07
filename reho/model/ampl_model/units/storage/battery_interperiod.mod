#####################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Battery (adapted to inter-period storage)
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

#-First-order electrical storage model including:
#	1. dis-/charging efficiencies 
#	2. self-discharging efficiency 
#	3. dis-/charging limits
#-References : 
# [1]	F. Oldewurtel et al., Building Control and Storage Management with [...], 2010 
# [2]   M. Koller et al., Defining a Degradation Cost Function for Optimal [...], 2013

#-Adapted model to additionally include :
# [3] Efficiency degradation over time (efficiency used is an average of the battery efficiency over its lifetime)
# [4] C-rate limitation (beware that maximum C-rate value is 1 (due to hourly resolution))

param BAT_eff_RTE_basis_IP{u in UnitsOfType['Battery_interperiod']} 	default 0.86;	#- AC-AC efficiency
param BAT_limit_ch_IP{u in UnitsOfType['Battery_interperiod']} default 0.8;			#-	[2]
param BAT_limit_di_IP{u in UnitsOfType['Battery_interperiod']} default 0.2;			#-	[1]
param C_rate_IP{u in UnitsOfType['Battery_interperiod']} default 1;					#-
param BAT_self_discharge_IP{u in UnitsOfType['Battery_interperiod']} default 0.99992;	#-	[1]
param BAT_RTE_degradation_IP{u in UnitsOfType['Battery_interperiod']} default 0.005; # Battery efficiency degradation per year
param BAT_efficiency_IP{u in UnitsOfType['Battery_interperiod']} >=0, <= sqrt(BAT_eff_RTE_basis_IP[u]) := sqrt(BAT_eff_RTE_basis_IP[u]-BAT_RTE_degradation_IP[u]*lifetime[u]/2); #Computation of the one way efficiency (assuming equal efficiency out and in)
var BAT_E_stored_IP{h in House, u in UnitsOfType['Battery_interperiod'] inter UnitsOfHouse[h], hy in Year} >= 0;

#--Hourly Energy balance (valid for inter-period storage)
subject to BAT_energy_balance_IP{h in House,u in UnitsOfType['Battery_interperiod'] inter UnitsOfHouse[h], hy in Year}:
(BAT_E_stored_IP[h,u,next(hy,Year)] - BAT_self_discharge_IP[u]*BAT_E_stored_IP[h,u,hy]) = 
	(BAT_efficiency_IP[u]*Units_demand['Electricity',u,PeriodOfYear[hy],TimeOfYear[hy]]
	- (1/BAT_efficiency_IP[u])*Units_supply['Electricity',u,PeriodOfYear[hy],TimeOfYear[hy]] )*dt[PeriodOfYear[hy]];

#--SoC constraints
subject to BAT_c1_IP{h in House,u in UnitsOfType['Battery_interperiod'] inter UnitsOfHouse[h], hy in Year}:
BAT_E_stored_IP[h,u,hy] <= BAT_limit_ch_IP[u]*Units_Mult[u];

subject to BAT_c2_IP{h in House,u in UnitsOfType['Battery_interperiod'] inter UnitsOfHouse[h], hy in Year}:
BAT_E_stored_IP[h,u,hy] >= BAT_limit_di_IP[u]*Units_Mult[u];

#-- Power constraints
subject to BAT_c3_IP{h in House,u in UnitsOfType['Battery_interperiod'] inter UnitsOfHouse[h],p in PeriodStandard,t in Time[p]}:
Units_demand['Electricity',u,p,t]*dt[p] <= (BAT_limit_ch_IP[u]-BAT_limit_di_IP[u])*Units_Mult[u]*C_rate_IP[u];

subject to BAT_c4_IP{h in House,u in UnitsOfType['Battery_interperiod'] inter UnitsOfHouse[h],p in PeriodStandard,t in Time[p]}:
Units_supply['Electricity',u,p,t]*dt[p] <= (BAT_limit_ch_IP[u]-BAT_limit_di_IP[u])*Units_Mult[u]*C_rate_IP[u];
