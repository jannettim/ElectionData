import pandas as pd
import os
import re
import sqlite3
from numpy import nan
from lxml import etree
import requests


def create_database(db_path):

    cnxn = sqlite3.connect(db_path)
    cn = cnxn.cursor()

    cn.execute("DROP TABLE IF EXISTS elections")
    cn.execute("DROP TABLE IF EXISTS results")
    cnxn.commit()

    cn.execute("CREATE TABLE elections (Election_Id INTEGER PRIMARY KEY NOT NULL, "
               "State TEXT NOT NULL, District VARCHAR2(30) NOT NULL, Year INTEGER NOT NULL, Total_Votes REAL NOT NULL,"
               "Federal INTEGER NOT NULL "
               "CHECK(Federal in (0, 1)))")

    cn.execute("CREATE TABLE results (Election_Id INTEGER NOT NULL, Party TEXT NOT NULL, Votes INTEGER NOT NULL, "
               "Incumbent INTEGER, "
               "CHECK(Incumbent in (0, 1) OR Incumbent IS NULL), "
               #"PRIMARY KEY(Election_Id, Party), "
               "FOREIGN KEY(Election_Id) REFERENCES elections(Election_Id)) ")

    cnxn.commit()

    cn.close()
    cnxn.close()


def import_ispsr(directory):

    dir_files = [d for d in os.listdir(directory) if re.match(r"DS\d{1,4}", d) and d != "DS0049"]

    df = pd.DataFrame()

    year_lookup = pd.read_excel("data/ICPSR_06311/FolderCode_Year_Lookup.xlsx", "Sheet1")
    year_lookup["Code"] = year_lookup["Code"].astype(str).str.zfill(4)

    state_lookup = pd.read_excel("data/ICPSR_06311/Code_StateLookup.xlsx", "Sheet1")

    for d in dir_files:

        year = year_lookup.loc[year_lookup.Text.str.cat(year_lookup.Code) == d]["Year"].values[0]

        df2 = pd.read_csv(os.path.join(directory, d, os.listdir(os.path.join(directory, d))[0]), sep="\s+",
                         names=["State_Code", "District", "Incumbent", "Republican Votes", "Democratic Votes"])
        df2["Year"] = year

        df = df.append(df2)

    df = pd.merge(df, state_lookup, left_on="State_Code", right_on="Code", how="left")

    df.reset_index(inplace=True)

    df.rename(columns={"index": "Election_Id"}, inplace=True)

    df["Election_Id"] = df["Election_Id"] + 1

    elections = df[["Election_Id", "State", "District", "Year"]]

    dem_votes = df[["Election_Id", "Democratic Votes"]]
    dem_votes["Incumbent"] = 0
    dem_votes.loc[df["Election_Id"].isin(df.loc[((df["Incumbent"] == 1) | (df["Incumbent"] == 3))]["Election_Id"].tolist()), "Incumbent"] = 1
    dem_votes.rename(columns={"Democratic Votes": "Votes"}, inplace=True)
    dem_votes["Party"] = "Democrat"

    repub_votes = df[["Election_Id", "Republican Votes"]]
    repub_votes["Incumbent"] = 0
    repub_votes.loc[df["Election_Id"].isin(df.loc[((df["Incumbent"] == -1) | (df["Incumbent"] == 3))]["Election_Id"].tolist()), "Incumbent"] = 1
    repub_votes.rename(columns={"Republican Votes": "Votes"}, inplace=True)
    repub_votes["Party"] = "Republican"

    # print(dem_votes)
    # print(repub_votes)

    results = dem_votes.append(repub_votes)

    results.sort_values("Election_Id", inplace=True)
    results = results.loc[~results["Election_Id"].isin(results.loc[results["Votes"] == -9]["Election_Id"])]

    elections = elections.loc[~elections["Election_Id"].isin(results.loc[results["Votes"] == -9]["Election_Id"])]

    # print(os.path.join(directory, "DS0049", os.listdir(os.path.join(directory, "DS0049"))[0]))
    # exceptions = pd.read_csv(os.path.join(directory, "DS0049", os.listdir(os.path.join(directory, "DS0049"))[0]),
    #                          sep="\s+", skiprows=1,
    #                          names=["Year", "State", "District", "Democratic", "Republican", "Minor", "Total Votes"])
    # print(exceptions)
    #
    return elections, results


def clean_cq_data(datafile, sheet):

    df = pd.read_excel(datafile, sheet, skiprows=4, names=["State_Abbr", "District", "Dem_Can", "Dem_Votes",
                                                           "Dem_Per", "Rep_Can", "Rep_Votes", "Rep_Per",
                                                           "Highest_Minor", "Minor_Votes", "Minor %", "Year"],
                       skip_footer=2)
    df.loc[df.District == "At Large", "District"] = 98

    state_name = pd.read_excel("data/StateAbbr_Name_Lookup.xlsx", "Sheet1")
    df = pd.merge(df, state_name, how="left", on=["State_Abbr"])

    df.reset_index(inplace=True)
    df.rename(columns={"index": "Election_Id"}, inplace=True)

    df["Election_Id"] = df["Election_Id"] + 1

    elections = df[["Election_Id", "State", "District", "Year"]]
    elections["Federal"] = 1

    dem_votes = df[["Election_Id", "Dem_Votes"]]
    dem_votes.rename(columns={"Dem_Votes": "Votes"}, inplace=True)
    dem_votes["Party"] = "Democrat"
    dem_votes["Incumbent"] = nan

    rep_votes = df[["Election_Id", "Rep_Votes"]]
    rep_votes.rename(columns={"Rep_Votes": "Votes"}, inplace=True)
    rep_votes["Party"] = "Republican"
    rep_votes["Incumbent"] = nan

    other_votes = df[["Election_Id", "Minor_Votes"]]
    other_votes.rename(columns={"Minor_Votes": "Votes"}, inplace=True)
    other_votes["Party"] = "Other"
    other_votes["Incumbent"] = nan

    rep_votes["Votes"].fillna(0, inplace=True)
    dem_votes["Votes"].fillna(0, inplace=True)
    other_votes["Votes"].fillna(0, inplace=True)

    results = dem_votes.append(rep_votes)
    results = results.append(other_votes)
    results.sort_values(by="Election_Id", inplace=True)

    return elections, results

def import_klarner(datafile):

    df = pd.read_csv(datafile, sep="\t")

    # df = df.append(pd.read_csv("/home/matt/GitRepos/ElectionData/data/Klarner/SLERs2011to2012_only_2013_05_14.tab",
    #                            sep="\t"))

    df = df[["v01", "v02", "v03", "v04", "v05", "v06", "v07", "v08", "v09", "v11", "v12", "v16", "v18", "v19", "v21",
             "v22", "v23", "v24", "v25", "v29", "v30", "v31"]]

    df.rename(columns={"v01": "ID", "v02": "State_Abbr", "v03": "State_FIPS",
                       "v04": "State_Code_ICPSR", "v05": "Year", "v06": "Month", "v07": "House_Senate",
                       "v08": "District_Name",
                       "v09": "District_Id", "v11": "District", "v12": "District_Type", "v16": "Election_Type",
                       "v18": "Candidate_id", "v19": "Candidate_Name", "v21": "Party_Code", "v22": "Incumbent",
                       "v23": "Votes", "v24": "Election_Outcome", "v29": "Total_Votes", "v30": "Total_Votes_Dem",
                       "v31": "Total_Votes_Rep", "v25": "Candidate_Num"},
              inplace=True)

    df = df.merge(df[["State_Abbr", "District", "Year"]].drop_duplicates().reset_index(),
                  on=["State_Abbr", "District", "Year"])

    df.loc[df.index, "index"] = df["index"] + 1

    df.rename(columns={"index": "Election_Id"}, inplace=True)

    df = df.loc[df.Election_Type == "G"]
    df = df.loc[df.District_Type == 1]
    df = df.loc[~df.Total_Votes.isnull()]
    df = df.loc[df.Candidate_Num > 1]
    df = df.loc[(df.House_Senate == 9) | (df.State_Abbr == "NE")]

    df.loc[~df.Party_Code.isin([100, 200]), "Party"] = "Other"
    df.loc[df.Party_Code == 100, "Party"] = "Democrat"
    df.loc[df.Party_Code == 200, "Party"] = "Republican"

    # df.reset_index(inplace=True)
    #
    # df.rename(columns={"index": "Election_Id"}, inplace=True)
    #
    # df["Election_Id"] += 1

    elections = df[["Election_Id", "State_Abbr", "District", "Year", "Total_Votes"]]
    elections.loc[elections.index, "Federal"] = 0
    elections.drop_duplicates(subset=["State_Abbr", "District", "Year"], inplace=True)

    results = df[["Election_Id", "Votes", "Party", "Incumbent"]]
    results = results.groupby(["Election_Id", "Party"], as_index=False).sum()
    results.loc[results["Incumbent"] > 1, "Incumbent"] = 1

    results = results[["Election_Id", "Votes", "Party", "Incumbent"]]

    return elections, results


def import_princeton(datafile):

    df = pd.read_csv(datafile)

    df.loc[df.index, "Republican Votes"] = df["Republican Votes"].str.replace(",", "").astype(float)
    df.loc[df.index, "Democratic Votes"] = df["Democratic Votes"].str.replace(",", "").astype(float)

    df.reset_index(inplace=True)

    df.rename(columns={"index": "Election_Id"}, inplace=True)

    df.loc[df.index, "Election_Id"] += 1

    elections = df[["Election_Id", "State", "District", "Year"]]
    elections.loc[elections.index, "Federal"] = 1

    dem_votes = df[["Election_Id", "Democratic Votes"]]
    dem_votes.loc[dem_votes.index, "Party"] = "Democrat"
    dem_votes.rename(columns={"Democratic Votes": "Votes"}, inplace=True)

    rep_votes = df[["Election_Id", "Republican Votes"]]
    rep_votes.loc[rep_votes.index, "Party"] = "Republican"
    rep_votes.rename(columns={"Republican Votes": "Votes"}, inplace=True)

    results = dem_votes.append(rep_votes)
    results.loc[results.index, "Incumbent"] = nan
    results.sort_values(by="Election_Id", inplace=True)

    elections = elections.merge(results.groupby(["Election_Id"], as_index=False)["Votes"].sum(), how="inner",
                                on=["Election_Id"])

    elections = elections[["Election_Id", "State", "District", "Year", "Votes", "Federal"]]

    return elections, results


def import_princeton_state(datafiles):

    cnxn = sqlite3.connect("house_elections.db")
    cn = cnxn.cursor()

    if isinstance(datafiles, (list,tuple)):

        df = pd.DataFrame()

        for d in datafiles:

            df = df.append(pd.read_csv(d))

    else:

        df = pd.read_csv(datafiles)

    df.reset_index(df, inplace=True)
    df.drop("index", axis=1, inplace=True)

    cn.execute("SELECT MAX(Election_Id) FROM Elections")

    df["Election_Id"] = df.index + 1 + cn.fetchone()[0]

    df.rename(columns={"State": "State_Abbr"}, inplace=True)
    state_name = pd.read_excel("data/StateAbbr_Name_Lookup.xlsx", "Sheet1")
    df = pd.merge(df, state_name, how="left", on=["State_Abbr"])

    elections = df[["Election_Id", "State", "District", "Year"]]

    elections["Federal"] = 0

    dem_votes = df[["Election_Id", "Dem Votes", "Incumbent"]]
    dem_votes.loc[dem_votes.index, "Party"] = "Democrat"
    dem_votes.rename(columns={"Dem Votes": "Votes"}, inplace=True)

    rep_votes = df[["Election_Id", "GOP Votes", "Incumbent"]]
    rep_votes.loc[rep_votes.index, "Party"] = "Republican"
    rep_votes.rename(columns={"GOP Votes": "Votes"}, inplace=True)

    other_votes = df[["Election_Id", "Other Votes", "Incumbent"]]
    other_votes.loc[other_votes.index, "Party"] = "Other"
    other_votes.rename(columns={"Other Votes": "Votes"}, inplace=True)

    results = dem_votes.append(rep_votes)
    results = results.append(other_votes)
    results = results[["Election_Id", "Votes", "Party", "Incumbent"]]
    results.sort_values(by="Election_Id", inplace=True)

    elections = elections.merge(results.groupby(["Election_Id"], as_index=False)["Votes"].sum(), how="inner",
                                on=["Election_Id"])

    elections = elections[["Election_Id", "State", "District", "Year", "Votes", "Federal"]]

    return elections, results


def insert_princeton(elections_df, results_df):

    cnxn = sqlite3.connect("house_elections.db")
    cn = cnxn.cursor()

    cn.executemany("INSERT INTO elections (Election_Id, State, District, Year, Total_Votes, Federal) "
                   "VALUES (?, ?, ?, ?, ?, ?)", elections_df.values.tolist())

    cnxn.commit()

    cn.executemany("INSERT INTO results (Election_Id, Votes, Party, Incumbent) "
                   "VALUES (?, ?, ?, ?)", results_df.values.tolist())

    cnxn.commit()

    cn.close()
    cnxn.close()

if __name__ == "__main__":


    create_database("house_elections.db")
    # icpsr = import_ispsr("/home/matt/GitRepos/ElectionData/data/ICPSR_06311")
    # print(icpsr)
    # elections, results = clean_cq_data(datafile="data/CQ Press/House Elections/US House Elections By Year By District.xlsx", sheet="Export")
    elections, results = import_princeton("/home/matt/GitRepos/ElectionData/data/Princeton/election_data.csv")
    insert_princeton(elections, results)
    state_elections, state_results = import_princeton_state(["/home/matt/GitRepos/ElectionData/data/Princeton/assembly_cleaned_data_1972_2010.csv",
                                                             "/home/matt/GitRepos/ElectionData/data/Princeton/assembly_cleaned_data_2011_2012.csv"])
    # state_elections, state_results = import_klarner(
    #     "/home/matt/GitRepos/ElectionData/data/Klarner/SLERs1967to2010_2012_05_26.tab")
    insert_princeton(state_elections, state_results)