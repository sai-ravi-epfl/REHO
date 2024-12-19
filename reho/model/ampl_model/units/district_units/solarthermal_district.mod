######################################################################################################################
#--------------------------------------------------------------------------------------------------------------------#
# Solar thermal collector district
#--------------------------------------------------------------------------------------------------------------------#
######################################################################################################################

#-Static solar thermal panel model including:
#	1. temperature dependent efficiency and output
#-References : 
# [1]	J. Rager, PhD Thesis, 2015.
# [2]	J. Duffie and W. Beckmann, Solar Engineering of Thermal Processes, 4th edition, pp. 294.

# -------------------------------------------- SETS ------------------------------------------
param STC_dTmin_district := 7;
set STCindex_district ordered by Reals:= {55 + STC_dTmin_district};


param STC_module_size_district{u in UnitsOfType['ThermalSolar_district']}>=0 default 2.32;		#m2		Viessmann
param STC_a_district{u in UnitsOfType['ThermalSolar_district']}>=0 default 4.16;				#W/m2 K 	SPF (Viessmann, Vitosol 200-F)
param STC_b_district{u in UnitsOfType['ThermalSolar_district']}>=0 default 0.0073;				#W/m2 K2	SPF (Viessmann, Vitosol 200-F)
param STC_efficiency_ref_district{u in UnitsOfType['ThermalSolar_district']}>=0 default 0.836;	#-			SPF (Viessmann, Vitosol 200-F)

/*
#-Definition from [2]
param STC_efficiency_district{u in UnitsOfType['ThermalSolar_district'],T in STCindex_district,p in Period,t in Time[p]} :=
if I_global_STC[p,t] >0 and STC_efficiency_ref_district[u] - STC_a_district[u]*(STC_Tlm_district[p,t]/I_global_STC[p,t]) - STC_b_district[u]*(STC_Tlm_district[p,t]^2/I_global_STC[p,t]) > 0 then 
	STC_efficiency_ref_district[u] - STC_a_district[u]*(STC_Tlm_district[p,t]/I_global_STC[p,t]) - STC_b_district[u]*(STC_Tlm_district[p,t]^2/I_global_STC[p,t]) 
else 
	0;
*/

var STC_Area_T_district{u in UnitsOfType['ThermalSolar_district']}>= 0;

subject to STC_energy_balance_district{u in UnitsOfType['ThermalSolar_district'],T in STCindex_district,p in Period,t in Time[p]}:
Units_supply['Heat',u,p,t] = STC_Area_T_district[u]*STC_efficiency_district[p,t]*(I_global_STC[p,t]/1000);


#--Sizing
subject to STC_c1_district{u in UnitsOfType['ThermalSolar_district'],p in Period,t in Time[p]}:
STC_Area_T_district[u] = Units_Mult[u];																	#m2


	