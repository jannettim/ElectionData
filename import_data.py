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
               "State TEXT NOT NULL, District VARCHAR2(30) NOT NULL, Year INTEGER NOT NULL, Federal INTEGER NOT NULL "
               "CHECK(Federal in (0, 1)))")

    cn.execute("CREATE TABLE results (Election_Id INTEGER NOT NULL, Party TEXT NOT NULL, Votes INTEGER NOT NULL, "
               "Incumbent INTEGER, "
               "CHECK(Incumbent in (0, 1) OR Incumbent IS NULL), "
               "PRIMARY KEY(Election_Id, Party), "
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

    # dem_votes = df[["Election_Id", "Dem_Votes"]]
    # dem_votes["Incumbent"] = 0
    # dem_votes.loc[df["Election_Id"].isin(
    #     df.loc[((df["Incumbent"] == 1) | (df["Incumbent"] == 3))]["Election_Id"].tolist()), "Incumbent"] = 1
    # dem_votes.rename(columns={"Democratic Votes": "Votes"}, inplace=True)
    # dem_votes["Party"] = "Democrat"
    #
    # repub_votes = df[["Election_Id", "Republican Votes"]]
    # repub_votes["Incumbent"] = 0
    # repub_votes.loc[df["Election_Id"].isin(
    #     df.loc[((df["Incumbent"] == -1) | (df["Incumbent"] == 3))]["Election_Id"].tolist()), "Incumbent"] = 1
    # repub_votes.rename(columns={"Republican Votes": "Votes"}, inplace=True)
    # repub_votes["Party"] = "Republican"

    # print(dem_votes)
    # print(repub_votes)

    # results = dem_votes.append(repub_votes)

    # results.sort_values("Election_Id", inplace=True)
    #
    # print(df)
    #
    # 1/0

    # print(df.Dem_Votes + df.Rep_Votes + df.Minor_Votes)
    df["Total_Votes"] = df[["Dem_Votes", "Rep_Votes", "Minor_Votes"]].sum(axis=1)
    df["Losing Wasted Votes"] = df["Total_Votes"] - df[["Dem_Votes", "Rep_Votes", "Minor_Votes"]].max(axis=1)

    df["Winning Wasted Votes"] = df[["Dem_Votes", "Rep_Votes", "Minor_Votes"]].max(axis=1) + df["Total_Votes"]/2

    print(df[["Losing Wasted Votes", "Winning Wasted Votes"]])


def import_princeton(datafile):

    df = pd.read_csv(datafile)

    df["Republican Votes"] = df["Republican Votes"].str.replace(",", "")
    df["Democratic Votes"] = df["Democratic Votes"].str.replace(",", "")

    df.reset_index(inplace=True)

    df.rename(columns={"index": "Election_Id"}, inplace=True)

    df["Election_Id"] += 1

    elections = df[["Election_Id", "State", "District", "Year"]]
    elections["Federal"] = 1

    dem_votes = df[["Election_Id", "Democratic Votes"]]
    dem_votes["Party"] = "Democrat"
    dem_votes.rename(columns={"Democratic Votes": "Votes"}, inplace=True)

    rep_votes = df[["Election_Id", "Republican Votes"]]
    rep_votes["Party"] = "Republican"
    rep_votes.rename(columns={"Republican Votes": "Votes"}, inplace=True)

    results = dem_votes.append(rep_votes)
    results["Incumbent"] = nan
    results.sort_values(by="Election_Id", inplace=True)

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
    dem_votes["Party"] = "Democrat"
    dem_votes.rename(columns={"Dem Votes": "Votes"}, inplace=True)

    rep_votes = df[["Election_Id", "GOP Votes", "Incumbent"]]
    rep_votes["Party"] = "Republican"
    rep_votes.rename(columns={"GOP Votes": "Votes"}, inplace=True)

    other_votes = df[["Election_Id", "Other Votes", "Incumbent"]]
    other_votes["Party"] = "Other"
    other_votes.rename(columns={"Other Votes": "Votes"}, inplace=True)

    results = dem_votes.append(rep_votes)
    results = results.append(other_votes)
    results = results[["Election_Id", "Votes", "Party", "Incumbent"]]
    results.sort_values(by="Election_Id", inplace=True)

    return elections, results


def insert_princeton(elections_df, results_df):

    cnxn = sqlite3.connect("house_elections.db")
    cn = cnxn.cursor()

    cn.executemany("INSERT INTO elections (Election_Id, State, District, Year, Federal) "
                   "VALUES (?, ?, ?, ?, ?)", elections_df.values.tolist())

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
    # clean_cq_data(datafile="data/CQ Press/House Elections/US House Elections By Year By District.xlsx", sheet="Export")
    elections, results = import_princeton("/home/matt/GitRepos/ElectionData/data/Princeton/election_data.csv")
    insert_princeton(elections, results)
    state_elections, state_results = import_princeton_state(["/home/matt/GitRepos/ElectionData/data/Princeton/assembly_cleaned_data_1972_2010.csv",
                                                             "/home/matt/GitRepos/ElectionData/data/Princeton/assembly_cleaned_data_2011_2012.csv"])
    insert_princeton(state_elections, state_results)