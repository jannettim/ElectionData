import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from analysis import get_efficiency_gap

import pandas as pd
from numpy import nan
from linearmodels import PanelOLS


#############
###FEDERAL###
#############

starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]

# gaps = pd.concat([gaps, gaps["State"].str.get_dummies()[["Arizona", "California", "Idaho", "Washington", "Iowa"]]], axis=1)

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 0

for i, r in starts.iterrows():

    gaps.loc[(gaps.State == r["State"]), "t"] = gaps.Year-r["Year"]


gaps.loc[gaps.index, "e"] = 0
gaps.loc[gaps.t == 0, "e"] = 1
gaps.loc[gaps.index, "emax"] = 0
gaps.loc[gaps.t >= 6, "emax"] = 1
gaps.loc[gaps.index, "emin"] = 0
gaps.loc[gaps.t <= -6, "emin"] = 1


print(gaps)
1/0
# gaps["independent_commission"].fillna(0, inplace=True)


gaps = gaps.loc[~gaps.State.isin(["Alaska", "Delaware", "Montana", "North Dakota", "South Dakota", "Vermont", "Wyoming"])]
gaps.set_index(["State", "Year"], inplace=True)


model = PanelOLS.from_formula('gap ~ 1 + independent_commission + EntityEffects + TimeEffects', data=gaps)

#
# model = PanelOLS(gaps.gap, gaps[["independent_commission"]], entity_effects=True, time_effects=True)
print(model.fit(cov_type="robust"))


gaps["Washington"] = gaps["Washington"].multiply(gaps["independent_commission"])
gaps["Arizona"] = gaps["Arizona"].multiply(gaps["independent_commission"])
gaps["California"] = gaps["California"].multiply(gaps["independent_commission"])
gaps["Idaho"] = gaps["Idaho"].multiply(gaps["independent_commission"])
gaps["Iowa"] = gaps["Iowa"].multiply(gaps["independent_commission"])



# model = PanelOLS.from_formula('gap ~ 1 + independent_commission + EntityEffects + TimeEffects + Washington', data=gaps)
# print(model.fit(cov_type="robust"))
# model = PanelOLS.from_formula('gap ~ 1 + independent_commission + EntityEffects + TimeEffects + California', data=gaps)
# print(model.fit(cov_type="robust"))
# model = PanelOLS.from_formula('gap ~ 1 + independent_commission + EntityEffects + TimeEffects + Arizona', data=gaps)
# print(model.fit(cov_type="robust"))
# model = PanelOLS.from_formula('gap ~ 1 + independent_commission + EntityEffects + TimeEffects + Idaho', data=gaps)
# print(model.fit(cov_type="robust"))
# model = PanelOLS.from_formula('gap ~ 1 + independent_commission + EntityEffects + TimeEffects + Iowa', data=gaps)
# print(model.fit(cov_type="robust"))
1/0



###########
###STATE###
###########
starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("state")[['State', 'Year', 'gap']]

gaps["independent_commission"] = nan

print(gaps["State"].str.get_dummies()[["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]])

for i, r in starts.iterrows():

    gaps.loc[(gaps.State == r["State"]) & (gaps.Year >= r["Year"]), "independent_commission"] = 1

gaps["independent_commission"].fillna(0, inplace=True)
gaps = gaps.loc[~gaps.State.isin(["Alaska", "Delaware", "Montana", "North Dakota", "South Dakota", "Vermont", "Wyoming"])]
gaps.set_index(["State", "Year"], inplace=True)
gaps["gap"] = gaps["gap"].abs()

model = PanelOLS.from_formula('gap ~ 1 + independent_commission + EntityEffects + TimeEffects', data=gaps)

print(model.fit(cov_type="robust"))