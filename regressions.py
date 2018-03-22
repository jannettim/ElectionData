import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from analysis import get_efficiency_gap

import pandas as pd
from numpy import nan, mean
from linearmodels import PanelOLS


fips = pd.read_excel("/home/matt/GitRepos/ElectionData/data/State_FIPS.xlsx", "Sheet1")
fips.rename(columns={"Name": "State", "FIPS State Numeric Code": "FIPS", "Official USPS Code": "StateAbbr"},
            inplace=True)
fips["FIPS"] = fips["FIPS"].astype(str).str.zfill(2)

turnout = pd.read_excel("/home/matt/GitRepos/ElectionData/data/1980-2014 November General Election.xlsx", "Turnout Rates", skiprows=1)
turnout.drop(["Overseas Eligible"], axis=1, inplace=True)
turnout.rename(columns={"Unnamed: 3": "State", "VEP Total Ballots Counted": "TurnoutRate"}, inplace=True)
turnout = turnout[["State", "Year", "TurnoutRate"]]
turnout.dropna(inplace=True)


gov_party = pd.read_excel("/home/matt/GitRepos/ElectionData/data/StateElections_Gub_2012_09_06_Public_Version.xlsx", "govelections")
gov_party = gov_party[["state", "year", "govparty_b"]]
gov_party.dropna(inplace=True)

pres_party = pd.read_excel("/home/matt/GitRepos/ElectionData/data/PresidentParty_Year.xlsx", "Sheet1")

urban = pd.read_excel("/home/matt/GitRepos/ElectionData/data/pop-urban-pct-historical.xls", "States", skiprows=5,
                      skip_footer=7)
urban.drop(["Unnamed: 7", "Unnamed: 13"], axis=1, inplace=True)
urban.rename(columns = {"Area Name": "State"}, inplace=True)
urban = urban.melt(id_vars=["FIPS", "State"], var_name="Year", value_name="Per_Urban")

urban = urban.loc[urban.Year >= 1970]
for i in list(set(urban.Year.tolist())):

    for r in range(1, 10):
        temp_df = urban.loc[urban.Year == i]
        temp_df["Year"] = i + r
        urban = pd.concat([urban, temp_df])

urban = urban[["State", "Year", "Per_Urban"]]


anes = pd.read_csv("/home/matt/GitRepos/ElectionData/data/anes_timeseries_cdf/anes_timeseries_cdf_rawdata.txt", sep="|", na_values=[" "])
# anes.to_csv("/home/matt/GitRepos/ElectionData/data/anes_timeseries_cdf/rel_anes.csv")
# anes = pd.read_csv("/home/matt/GitRepos/ElectionData/data/anes_timeseries_cdf/rel_anes.csv")
# anes["VCF0170d"] = anes["VCF0170d"].str.replace("^\s+$", nan)
anes = anes[["VCF0004", "VCF0901a", "VCF0301", "VCF0703", "VCF0305"]]
anes.dropna(inplace=True)
anes.rename(columns={"VCF0004": "Year", "VCF0901a": "FIPS", "VCF0301": "Partisan7", "VCF0703": "Voting_Info",
                     "VCF0305": "Partisan4"}, inplace=True)


anes.loc[anes.Voting_Info != 3, "Voted"] = 0
anes.loc[anes.Voting_Info == 3, "Voted"] = 1

anes.loc[(anes.Voting_Info != 2) | (anes.Voting_Info != 3), "Registered"] = 0
anes.loc[(anes.Voting_Info == 2) | (anes.Voting_Info == 3), "Registered"] = 1

anes.loc[anes.Partisan4 < 3, "Partisan"] = 0
anes.loc[anes.Partisan4 >= 3, "Partisan"] = 1
percents = anes.groupby(["Year", "FIPS"], as_index=False)[["Partisan", "Voted", "Registered"]].mean()

turn_calc = anes.groupby(["Year", "FIPS"], as_index=False)[["Voted", "Registered"]].sum()
turn_calc["Registered_Turnout"] = turn_calc["Voted"]/turn_calc["Registered"]

anes_final = percents.merge(turn_calc[["Year", "FIPS", "Registered_Turnout"]], on=["Year", "FIPS"], how="inner")
anes_final["FIPS"] = anes_final["FIPS"].astype(str).str.zfill(2)
anes_final = anes_final.merge(fips, on=["FIPS"], how="left")
anes_final = anes_final[["Year", "State", "Partisan", "Voted", "Registered", "Registered_Turnout"]]

anes_2016 = pd.read_csv("/home/matt/GitRepos/ElectionData/data/anes_timeseries_cdf/anes_timeseries_2016/anes_timeseries_2016_rawdata.txt", sep="|", na_values=[" "])
anes_2016 = anes_2016[["V161156", "V161010d", "V162034", "V162022", "V161011"]]
anes_2016["Year"] = 2016
anes_2016.rename(columns={"V161010d": "FIPS", "V162034": "Voting_Info", "V161156": "partisanship_info",
                          "V162022": "Registered_Post", "V161011": "Registered_Pre"}, inplace=True)
anes_2016["FIPS"] =anes_2016["FIPS"].astype(str).str.zfill(2)
anes_2016.loc[anes_2016.Voting_Info != 1, "Voted"] = 0
anes_2016.loc[anes_2016.Voting_Info == 1, "Voted"] = 1
anes_2016.dropna(inplace=True)

anes_2016.loc[anes_2016["partisanship_info"] != 2, "Partisan"] = 0
anes_2016.loc[anes_2016["partisanship_info"] == 2, "Partisan"] = 1

anes_2016.loc[((anes_2016["Registered_Pre"] != 1) & (anes_2016["Registered_Pre"] != 2)) &
              ((anes_2016["Registered_Post"] != 1) & (anes_2016["Registered_Post"] != 2)), "Registered"] = 0

anes_2016.loc[((anes_2016["Registered_Pre"] == 1) | (anes_2016["Registered_Pre"] == 2)) |
              ((anes_2016["Registered_Post"] == 1) | (anes_2016["Registered_Post"] == 2)), "Registered"] = 1


anes_2016 = anes_2016[["FIPS", "Year", "Voted", "Partisan", "Registered"]]

percents_2016 = anes_2016.groupby(["Year", "FIPS"], as_index=False)[["Voted", "Partisan", "Registered"]].mean()
turn_calc_2016 = anes_2016.groupby(["Year", "FIPS"], as_index=False)[["Voted", "Registered"]].sum()
turn_calc_2016["Registered_Turnout"] = turn_calc_2016["Voted"]/turn_calc_2016["Registered"]
anes_2016 = percents_2016.merge(turn_calc_2016[["Year", "FIPS", "Registered_Turnout"]], on=["Year", "FIPS"], how="inner")
anes_2016 = anes_2016.merge(fips, on=["FIPS"], how="left")
anes_2016 = anes_2016[["Year", "State", "Partisan", "Voted", "Registered", "Registered_Turnout"]]

anes_final = anes_final.append(anes_2016)

# print(anes_final["Year"].value_counts())



########################
###SYNTH CONTROL PREP###
########################

#############
###FEDERAL###
#############

starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 0


unemp_1976 = pd.read_excel("/home/matt/GitRepos/ElectionData/data/LAUS_Unemp_1976-1994.xlsx", "BLS Data Series", skiprows=3)
unemp_1995 = pd.read_excel("/home/matt/GitRepos/ElectionData/data/LAUS_Unemp_1995-2013.xlsx", "BLS Data Series", skiprows=3)
unemp_2014 = pd.read_excel("/home/matt/GitRepos/ElectionData/data/LAUS_Unemp_2014-2018.xlsx", "BLS Data Series", skiprows=3)
unemp_2014.dropna(axis=1, inplace=True)

unemp_1976 = unemp_1976.filter(regex="Annual|Series")
unemp_1995 = unemp_1995.filter(regex="Annual|Series")
unemp_2014 = unemp_2014.filter(regex="Annual|Series")

unemp = unemp_1976.merge(unemp_1995, on="Series ID", how="inner")
unemp = unemp.merge(unemp_2014, on="Series ID", how="inner")

unemp.columns = unemp.columns.str.replace(r"\s", "")

unemp["FIPS"] = unemp["SeriesID"].str[5:7]

unemp = unemp.merge(fips, on="FIPS", how="inner")

unemp.drop(["FIPS", "StateAbbr", "SeriesID"], inplace=True, axis=1)

unemp = unemp.melt(id_vars=["State"], var_name="Year", value_name="UnempRate")

unemp["Year"] = unemp["Year"].str.replace("Annual", "").astype(int)

gaps = gaps.merge(unemp, how="left", on=["State", "Year"])
gaps = gaps.merge(anes_final, how="left", on=["State", "Year"])
gaps = gaps.merge(urban, how="left", on=["State", "Year"])
gaps = gaps.merge(pres_party, how="left", on=["Year"])
gaps = gaps.merge(gov_party, how="left", left_on=["State", "Year"], right_on=["state", "year"])
gaps.to_csv("federal_synth.csv")
gaps.dropna(inplace=True)

gaps["gap"] = gaps["gap"].abs()

test = pd.DataFrame([tuple([x, ]) for x in range(1976, 2017, 2)], columns=["Year"])

test = test.merge(gaps, how="left", on="Year")

test.to_csv("test.csv")

gaps.to_csv("federal_synth.csv")



starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("state")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 0


unemp_1976 = pd.read_excel("/home/matt/GitRepos/ElectionData/data/LAUS_Unemp_1976-1994.xlsx", "BLS Data Series", skiprows=3)
unemp_1995 = pd.read_excel("/home/matt/GitRepos/ElectionData/data/LAUS_Unemp_1995-2013.xlsx", "BLS Data Series", skiprows=3)
unemp_2014 = pd.read_excel("/home/matt/GitRepos/ElectionData/data/LAUS_Unemp_2014-2018.xlsx", "BLS Data Series", skiprows=3)
unemp_2014.dropna(axis=1, inplace=True)

unemp_1976 = unemp_1976.filter(regex="Annual|Series")
unemp_1995 = unemp_1995.filter(regex="Annual|Series")
unemp_2014 = unemp_2014.filter(regex="Annual|Series")

unemp = unemp_1976.merge(unemp_1995, on="Series ID", how="inner")
unemp = unemp.merge(unemp_2014, on="Series ID", how="inner")

unemp.columns = unemp.columns.str.replace(r"\s", "")

unemp["FIPS"] = unemp["SeriesID"].str[5:7]

unemp = unemp.merge(fips, on="FIPS", how="inner")

unemp.drop(["FIPS", "StateAbbr", "SeriesID"], inplace=True, axis=1)

unemp = unemp.melt(id_vars=["State"], var_name="Year", value_name="UnempRate")

unemp["Year"] = unemp["Year"].str.replace("Annual", "").astype(int)

gaps = gaps.merge(unemp, how="left", on=["State", "Year"])
gaps = gaps.merge(anes_final, how="left", on=["State", "Year"])
gaps = gaps.merge(urban, how="left", on=["State", "Year"])
gaps = gaps.merge(pres_party, how="left", on=["Year"])
gaps = gaps.merge(gov_party, how="left", left_on=["State", "Year"], right_on=["state", "year"])
gaps.dropna(inplace=True)
gaps["gap"] = gaps["gap"].abs()

gaps.to_csv("state_synth.csv")



########################
######EVENT STUDY#######
########################

#############
###FEDERAL###
#############

starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 0

for i, r in starts.iterrows():

    gaps.loc[(gaps.State == r["State"]), "t"] = gaps.Year-r["Year"]

gaps = gaps.loc[(gaps.t >= -6) & (gaps.t <= 6)]

gaps.loc[gaps.index, "indcom_6"] = 0
gaps.loc[gaps.t == -6, "indcom_6"] = 1

gaps.loc[gaps.index, "indcom_4"] = 0
gaps.loc[gaps.t == -4, "indcom_4"] = 1

gaps.loc[gaps.index, "indcom_2"] = 0
gaps.loc[gaps.t == -2, "indcom_2"] = 1

gaps.loc[gaps.index, "indcom"] = 0
gaps.loc[gaps.t == 0, "indcom"] = 1

gaps.loc[gaps.index, "indcom1"] = 0
gaps.loc[gaps.t == 1, "indcom1"] = 1

gaps.loc[gaps.index, "indcom2"] = 0
gaps.loc[gaps.t == 2, "indcom2"] = 1

gaps.loc[gaps.index, "indcom4"] = 0
gaps.loc[gaps.t == 4, "indcom4"] = 1

gaps.loc[gaps.index, "indcom6"] = 0
gaps.loc[gaps.t == 6, "indcom6"] = 1


gaps = gaps.loc[~gaps.State.isin(["Alaska", "Delaware", "Montana", "North Dakota", "South Dakota", "Vermont", "Wyoming"])]
gaps.set_index(["State", "Year"], inplace=True)

gaps["gap"] = gaps["gap"].abs()

model = PanelOLS.from_formula('gap ~ 1 + indcom_4 + indcom_2 + indcom + indcom2 + indcom4 + indcom6', data=gaps)

print(model.fit(cov_type="robust"))



###########
###STATE###
###########

starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]),
         "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]),
         "independent_commission"] = 0

for i, r in starts.iterrows():

    gaps.loc[(gaps.State == r["State"]), "t"] = gaps.Year-r["Year"]

gaps = gaps.loc[(gaps.t >= -6) & (gaps.t <= 6)]

gaps.loc[gaps.index, "indcom_6"] = 0
gaps.loc[gaps.t == -6, "indcom_6"] = 1

gaps.loc[gaps.index, "indcom_4"] = 0
gaps.loc[gaps.t == -4, "indcom_4"] = 1

gaps.loc[gaps.index, "indcom_2"] = 0
gaps.loc[gaps.t == -2, "indcom_2"] = 1

gaps.loc[gaps.index, "indcom"] = 0
gaps.loc[gaps.t == 0, "indcom"] = 1

gaps.loc[gaps.index, "indcom1"] = 0
gaps.loc[gaps.t == 1, "indcom1"] = 1

gaps.loc[gaps.index, "indcom2"] = 0
gaps.loc[gaps.t == 2, "indcom2"] = 1

gaps.loc[gaps.index, "indcom4"] = 0
gaps.loc[gaps.t == 4, "indcom4"] = 1

gaps.loc[gaps.index, "indcom6"] = 0
gaps.loc[gaps.t == 6, "indcom6"] = 1


gaps = gaps.loc[~gaps.State.isin(["Delaware", "North Dakota", "South Dakota", "Vermont", "Wyoming"])]
gaps.set_index(["State", "Year"], inplace=True)

gaps["gap"] = gaps["gap"].abs()

model = PanelOLS.from_formula('gap ~ 1 + indcom_4 + indcom_2 + indcom + indcom2 + indcom4 + indcom6', data=gaps)

print(model.fit(cov_type="robust"))


##################
###DIFF-IN-DIFF###
##################


#############
###FEDERAL###
#############


starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 0

gaps.loc[gaps.Year < 1990, "Post"] = 0
gaps.loc[gaps.Year >= 1990, "Post"] = 1

gaps["Interact"] = gaps.Post * gaps["independent_commission"]


gaps = gaps.loc[gaps.State.isin(["Washington", "Oregon"])]

y = gaps["gap"].abs()
X = gaps.drop(["gap", "Year", "State"], axis=1)

X_cons = sm.add_constant(X)
lm = sm.OLS(y, X_cons).fit(cov_type="HC3")

print(lm.summary())



starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("Federal")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 0

gaps.loc[gaps.Year < 2002, "Post"] = 0
gaps.loc[gaps.Year >= 2002, "Post"] = 1

gaps["Interact"] = gaps.Post * gaps["independent_commission"]


gaps = gaps.loc[gaps.State.isin(["Arizona", "Texas"])]

y = gaps["gap"].abs()#.as_matrix()
X = gaps.drop(["gap", "Year", "State"], axis=1)#.as_matrix()

X_cons = sm.add_constant(X)
lm = sm.OLS(y, X_cons).fit(cov_type="HC3", use_t=True)

print(lm.summary())


#############
####STATE####
#############

starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("state")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 0

gaps.loc[gaps.Year < 1990, "Post"] = 0
gaps.loc[gaps.Year >= 1990, "Post"] = 1

gaps["Interact"] = gaps.Post * gaps["independent_commission"]


gaps = gaps.loc[gaps.State.isin(["Washington", "Oregon"])]

y = gaps["gap"].abs()
X = gaps.drop(["gap", "Year", "State"], axis=1)

X_cons = sm.add_constant(X)
lm = sm.OLS(y, X_cons).fit(cov_type="HC3")

print(lm.summary())



starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("state")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 0

gaps.loc[gaps.Year < 2002, "Post"] = 0
gaps.loc[gaps.Year >= 2002, "Post"] = 1

gaps["Interact"] = gaps.Post * gaps["independent_commission"]


gaps = gaps.loc[gaps.State.isin(["Arizona", "Texas"])]

y = gaps["gap"].abs()#.as_matrix()
X = gaps.drop(["gap", "Year", "State"], axis=1)#.as_matrix()

X_cons = sm.add_constant(X)
lm = sm.OLS(y, X_cons).fit(cov_type="HC3", use_t=True)

print(lm.summary())



#################
####BASIC OLS####
#################


#############
###FEDERAL###
#############


starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa"]), "independent_commission"] = 0

y = gaps["gap"].abs()
X = gaps.drop(["gap", "Year", "State"], axis=1)

X_cons = sm.add_constant(X)

lm = sm.OLS(y, X_cons).fit(cov_type="HC3", use_t=True)

print(lm.summary())


#############
####STATE####
#############


starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("state")[['State', 'Year', 'gap']]

gaps.loc[gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 1
gaps.loc[~gaps.State.isin(["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]), "independent_commission"] = 0

y = gaps["gap"].abs()
X = gaps.drop(["gap", "Year", "State"], axis=1)

X_cons = sm.add_constant(X)

lm = sm.OLS(y, X_cons).fit(cov_type="HC3", use_t=True)

print(lm.summary())


####################
####SEPARATE OLS####
####################


#############
###FEDERAL###
#############


starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("federal")[['State', 'Year', 'gap']]

for s in ["Arizona", "California", "Idaho", "Washington", "Iowa"]:

    start_year = starts.loc[starts.State == s, "Year"].values[0]

    state = gaps.loc[(gaps.State == s)]
    state.loc[state.Year >= start_year, "Post"] = 1
    state.loc[state.Year < start_year, "Post"] = 0

    y = state["gap"].abs()
    X = state.drop(["gap", "Year", "State"], axis=1)

    X_cons = sm.add_constant(X)

    lm = sm.OLS(y, X_cons).fit(cov_type="HC3", use_t=True)

    print(s)

    print(lm.summary())



#############
####STATE####
#############


starts = pd.read_excel("/home/matt/GitRepos/ElectionData/data/Independent_Commission_Start.xlsx", "Sheet1", skip_footer=2)
starts["time"] = 1

gaps = get_efficiency_gap("state")[['State', 'Year', 'gap']]

for s in ["Arizona", "California", "Idaho", "Washington", "Iowa", "Montana", "Alaska"]:

    start_year = starts.loc[starts.State == s, "Year"].values[0]

    state = gaps.loc[(gaps.State == s)]
    state.loc[state.Year >= start_year, "Post"] = 1
    state.loc[state.Year < start_year, "Post"] = 0

    y = state["gap"].abs()
    X = state.drop(["gap", "Year", "State"], axis=1)

    X_cons = sm.add_constant(X)

    lm = sm.OLS(y, X_cons).fit(cov_type="HC3", use_t=True)

    print(s)

    print(lm.summary())